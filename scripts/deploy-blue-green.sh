#!/bin/bash
# Blue-Green Deployment Script for AWS EC2 + ALB
# Usage: ./scripts/deploy-blue-green.sh --image-tag v1.2.3
#
# Required environment variables (set in GitHub Actions secrets):
#   EC2_BLUE_HOST      — Public IP of blue EC2 instance
#   EC2_GREEN_HOST     — Public IP of green EC2 instance
#   EC2_USER           — SSH user (ec2-user for Amazon Linux, ubuntu for Ubuntu)
#   SSH_KEY_PATH       — Path to PEM key file
#   ALB_LISTENER_ARN   — ARN of ALB HTTPS/HTTP listener
#   TG_BLUE_ARN        — ARN of Blue Target Group
#   TG_GREEN_ARN       — ARN of Green Target Group
#   AWS_REGION         — e.g. us-east-1
#   DOCKER_IMAGE       — e.g. yourdockerhub/cart-api
#   DATABASE_URL       — PostgreSQL RDS connection string

set -euo pipefail

GREEN_COLOR='\033[0;32m'
RED_COLOR='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

IMAGE_TAG="latest"
while [[ $# -gt 0 ]]; do
    case $1 in
        --image-tag) IMAGE_TAG="$2"; shift 2 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

log()  { echo -e "${GREEN_COLOR}[$(date '+%H:%M:%S')] $1${NC}"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] $1${NC}"; }
fail() { echo -e "${RED_COLOR}[$(date '+%H:%M:%S')] $1${NC}"; exit 1; }

# ── Step 1: Determine which slot is currently active ───────────────────────
log "Determining active slot..."

LISTENER_RULES=$(aws elbv2 describe-rules \
    --listener-arn "$ALB_LISTENER_ARN" \
    --region "$AWS_REGION" \
    --query 'Rules[?Priority==`1`].Actions[0].ForwardConfig.TargetGroups' \
    --output json 2>/dev/null || echo "[]")

BLUE_WEIGHT=$(echo "$LISTENER_RULES" | python3 -c "
import sys, json
rules = json.load(sys.stdin)
if not rules: print(100); exit()
for tg in rules[0]:
    if '$TG_BLUE_ARN' in tg.get('TargetGroupArn',''):
        print(tg.get('Weight', 0)); exit()
print(0)
" 2>/dev/null || echo "100")

if [ "$BLUE_WEIGHT" -ge 50 ]; then
    ACTIVE_SLOT="blue"
    INACTIVE_SLOT="green"
    ACTIVE_HOST="$EC2_BLUE_HOST"
    INACTIVE_HOST="$EC2_GREEN_HOST"
    ACTIVE_TG_ARN="$TG_BLUE_ARN"
    INACTIVE_TG_ARN="$TG_GREEN_ARN"
else
    ACTIVE_SLOT="green"
    INACTIVE_SLOT="blue"
    ACTIVE_HOST="$EC2_GREEN_HOST"
    INACTIVE_HOST="$EC2_BLUE_HOST"
    ACTIVE_TG_ARN="$TG_GREEN_ARN"
    INACTIVE_TG_ARN="$TG_BLUE_ARN"
fi

log "Active slot   : $ACTIVE_SLOT ($ACTIVE_HOST) ← serving live traffic"
log "Deploying to  : $INACTIVE_SLOT ($INACTIVE_HOST)"

# ── Step 2: Deploy new image to inactive slot ──────────────────────────────
log "Deploying image $DOCKER_IMAGE:$IMAGE_TAG to $INACTIVE_SLOT..."

ssh -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" "$EC2_USER@$INACTIVE_HOST" bash <<EOF
    set -e
    cd /home/$EC2_USER/app

    echo "Pulling new image..."
    export DOCKER_IMAGE="$DOCKER_IMAGE"
    export IMAGE_TAG="$IMAGE_TAG"
    export DATABASE_URL="$DATABASE_URL"

    docker pull "$DOCKER_IMAGE:$IMAGE_TAG"

    echo "Restarting container with new image..."
    docker-compose -f docker-compose.prod.yml up -d --force-recreate

    echo "Deploy to $INACTIVE_SLOT complete."
EOF

# ── Step 3: Health check inactive slot ────────────────────────────────────
log "Running health checks on $INACTIVE_SLOT ($INACTIVE_HOST)..."

INACTIVE_URL="http://$INACTIVE_HOST:8000"
HEALTHY=false

for i in $(seq 1 12); do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$INACTIVE_URL/docs" || echo "000")
    log "Health check attempt $i/12 → HTTP $STATUS"
    if [ "$STATUS" == "200" ]; then
        HEALTHY=true
        break
    fi
    sleep 15
done

if [ "$HEALTHY" != "true" ]; then
    fail "Health check FAILED on $INACTIVE_SLOT. $ACTIVE_SLOT remains live. No traffic switched."
fi

log "$INACTIVE_SLOT is healthy. Running smoke tests..."
bash "$(dirname "$0")/health_check.sh" "$INACTIVE_URL" || fail "Smoke test failed on $INACTIVE_SLOT."

# ── Step 4: Switch ALB traffic to inactive slot ────────────────────────────
log "Switching ALB traffic from $ACTIVE_SLOT → $INACTIVE_SLOT..."

aws elbv2 modify-listener \
    --listener-arn "$ALB_LISTENER_ARN" \
    --region "$AWS_REGION" \
    --default-actions "Type=forward,ForwardConfig={TargetGroups=[{TargetGroupArn=$INACTIVE_TG_ARN,Weight=100},{TargetGroupArn=$ACTIVE_TG_ARN,Weight=0}]}"

log "──────────────────────────────────────────────────────"
log "Blue-Green switch COMPLETE"
log "  NEW active  : $INACTIVE_SLOT ($INACTIVE_HOST)"
log "  NEW standby : $ACTIVE_SLOT   ($ACTIVE_HOST)"
log "  Image       : $DOCKER_IMAGE:$IMAGE_TAG"
log "──────────────────────────────────────────────────────"
