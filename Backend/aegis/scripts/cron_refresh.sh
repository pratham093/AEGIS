#!/usr/bin/env bash
# crontab: 30 17 * * 1-5 /path/to/cron_refresh.sh
set -euo pipefail

BACKEND="/Users/prathamshah/Desktop/CODE/AEGIS_V3/Backend"
VENV="$BACKEND/.venv/bin/python"
LOG_DIR="$BACKEND/logs"
LOG_FILE="$LOG_DIR/daily_refresh.log"

mkdir -p "$LOG_DIR"

echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "CRON RUN: $(date '+%Y-%m-%d %H:%M:%S %Z')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

"$VENV" -m aegis.scripts.daily_signals >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "FAILED (exit code $EXIT_CODE)" >> "$LOG_FILE"
else
    echo "SUCCESS" >> "$LOG_FILE"
fi

find "$LOG_DIR" -name "daily_refresh.log.*" -mtime +90 -delete 2>/dev/null || true

LOG_SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)
if [ "$LOG_SIZE" -gt 5242880 ]; then
    mv "$LOG_FILE" "$LOG_FILE.$(date '+%Y%m%d')"
fi

exit $EXIT_CODE
