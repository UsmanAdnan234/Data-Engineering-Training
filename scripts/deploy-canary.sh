#!/bin/bash
# Canary Deployment Script — gradual traffic shift via ALB weighted routing
# Usage: ./scripts/deploy-canary.sh --image-tag v1.2.3 --weight 10
#
# --weight options: 10 (10% canary), 50 (50% canary), 100 (full promotion)
#
# Required env vars: same as deploy-blue-green.sh

set -euo pipefail

GREEN_COLOR='\033[0;32m'
RED_COLOR='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

IMAGE_TAG="latest"
CANARY_WEIGHT=10

while [[ $# -gt 0 ]]; do
    case $1 in
        --image-tag)  IMAGE_TAG="$2";      shift 2 ;;
        --weight)     CANARY_WEIGHT="$2";  shift 2 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

STABLE_WEIGHT=$((100 - CANARY_WEIGHT))

log()  { echo -e "${GREEN_COLOR}[$(date '+%H:%M:%S')] $1${NC}"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] $1${NC}"; }
fail() { echo -e "${RED_COLOR}[$(date '+%H:%M:%S')] $1${NC}"; exit 1; }

rollback() {
    warn "ROLLBACK: resetting ALB to 100% blue (stable)..."
    aws elbv2 modify-listener \
        --listener-arn "$ALB_LISTENER_ARN" \
        --region "$AWS_REGION" \
        --default-actions "Type=forward,ForwardConfig={TargetGroups=[{TargetGroupArn=$TG_BLUE_ARN,Weight=100},{TargetGroupArn=$TG_GREEN_ARN,Weight=0}]}"
    warn "Rollback complete. Blue is 100% active."
}

trap rollback ERR

# ── Step 1: Deploy new image to green (canary) slot ───────────────────────
log "Deploying canary image $DOCKER_IMAGE:$IMAGE_TAG to green EC2..."

ssh -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" "$EC2_USER@$EC2_GREEN_HOST" bash <<EOF
    set -e
    cd /home/$EC2_USER/app
    export DOCKER_IMAGE="$DOCKER_IMAGE"
    export IMAGE_TAG="$IMAGE_TAG"
    export DATABASE_URL="$DATABASE_URL"
    docker pull "$DOCKER_IMAGE:$IMAGE_TAG"
    docker-compose -f docker-compose.prod.yml up -d --force-recreate
    echo "Canary deployed to green."
EOF

# ── Step 2: Health check green slot ───────────────────────────────────────
log "Health checking green (canary) slot..."

for i in $(seq 1 10); do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "http://$EC2_GREEN_HOST:8000/docs" || echo "000")
    log "Attempt $i/10 → HTTP $STATUS"
    if [ "$STATUS" == "200" ]; then break; fi
    if [ "$i" == "10" ]; then fail "Green slot never became healthy. Rollback triggered."; fi
    sleep 15
done

# ── Step 3: Set ALB weights ────────────────────────────────────────────────
log "Setting ALB: $STABLE_WEIGHT% blue (stable) / $CANARY_WEIGHT% green (canary)..."

aws elbv2 modify-listener \
    --listener-arn "$ALB_LISTENER_ARN" \
    --region "$AWS_REGION" \
    --default-actions "Type=forward,ForwardConfig={TargetGroups=[{TargetGroupArn=$TG_BLUE_ARN,Weight=$STABLE_WEIGHT},{TargetGroupArn=$TG_GREEN_ARN,Weight=$CANARY_WEIGHT}]}"

log "Traffic split: $STABLE_WEIGHT% stable blue → $CANARY_WEIGHT% canary green"

# ── Step 4: Monitor canary for 60 seconds ─────────────────────────────────
if [ "$CANARY_WEIGHT" -lt 100 ]; then
    log "Monitoring canary for 60 seconds (check CloudWatch for error spikes)..."
    sleep 60
    log "Monitoring window complete. No automated error detection — check CloudWatch alarms."
fi

# ── Step 5: Full promotion ─────────────────────────────────────────────────
if [ "$CANARY_WEIGHT" -eq 100 ]; then
    log "Promoting canary to 100%. Blue is now standby."
    aws elbv2 modify-listener \
        --listener-arn "$ALB_LISTENER_ARN" \
        --region "$AWS_REGION" \
        --default-actions "Type=forward,ForwardConfig={TargetGroups=[{TargetGroupArn=$TG_BLUE_ARN,Weight=0},{TargetGroupArn=$TG_GREEN_ARN,Weight=100}]}"
    log "Full promotion complete. Green is now 100% active."
fi

log "Canary deployment done. Weight=$CANARY_WEIGHT%"
