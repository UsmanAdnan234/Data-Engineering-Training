#!/bin/bash
# Rollback Script — ALB traffic, DB migration, or both
# Usage:
#   ./scripts/rollback.sh --mode alb   --alb-listener-arn ARN --stable-tg-arn ARN
#   ./scripts/rollback.sh --mode db    --db-url postgresql://...
#   ./scripts/rollback.sh --mode full  --alb-listener-arn ARN --stable-tg-arn ARN --canary-tg-arn ARN --db-url URL

set -euo pipefail

GREEN_COLOR='\033[0;32m'
RED_COLOR='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

MODE=""
ALB_LISTENER_ARN="${ALB_LISTENER_ARN:-}"
STABLE_TG_ARN="${TG_BLUE_ARN:-}"
CANARY_TG_ARN="${TG_GREEN_ARN:-}"
DB_URL="${DATABASE_URL:-}"
AWS_REGION="${AWS_REGION:-us-east-1}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)               MODE="$2";             shift 2 ;;
        --alb-listener-arn)   ALB_LISTENER_ARN="$2"; shift 2 ;;
        --stable-tg-arn)      STABLE_TG_ARN="$2";    shift 2 ;;
        --canary-tg-arn)      CANARY_TG_ARN="$2";    shift 2 ;;
        --db-url)             DB_URL="$2";            shift 2 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

log()  { echo -e "${GREEN_COLOR}[$(date '+%H:%M:%S')] $1${NC}"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] $1${NC}"; }
fail() { echo -e "${RED_COLOR}[$(date '+%H:%M:%S')] ERROR: $1${NC}"; exit 1; }

[ -z "$MODE" ] && fail "Must specify --mode (alb|db|full)"

rollback_alb() {
    [ -z "$ALB_LISTENER_ARN" ] && fail "--alb-listener-arn required for ALB rollback"
    [ -z "$STABLE_TG_ARN" ]    && fail "--stable-tg-arn required for ALB rollback"

    warn "About to switch 100% ALB traffic to stable target group."
    warn "Stable TG: $STABLE_TG_ARN"
    read -r -p "Confirm rollback? (yes/no): " CONFIRM
    [ "$CONFIRM" != "yes" ] && fail "Rollback cancelled."

    log "Switching ALB to 100% stable..."
    aws elbv2 modify-listener \
        --listener-arn "$ALB_LISTENER_ARN" \
        --region "$AWS_REGION" \
        --default-actions "Type=forward,ForwardConfig={TargetGroups=[{TargetGroupArn=$STABLE_TG_ARN,Weight=100},{TargetGroupArn=${CANARY_TG_ARN:-$STABLE_TG_ARN},Weight=0}]}"

    log "ALB rollback complete. 100% traffic on stable slot."
}

rollback_db() {
    [ -z "$DB_URL" ] && fail "--db-url required for DB rollback"

    warn "About to run: alembic downgrade -1 (rolls back ONE migration)"
    read -r -p "Confirm DB rollback? (yes/no): " CONFIRM
    [ "$CONFIRM" != "yes" ] && fail "DB rollback cancelled."

    log "Running alembic downgrade -1..."
    DATABASE_URL="$DB_URL" alembic downgrade -1
    log "DB rollback complete. Run 'alembic current' to verify."
}

case "$MODE" in
    alb)  rollback_alb ;;
    db)   rollback_db  ;;
    full) rollback_alb; rollback_db ;;
    *)    fail "Unknown mode: $MODE. Use alb, db, or full." ;;
esac

log "Rollback ($MODE) finished successfully."
