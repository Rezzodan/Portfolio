#!/bin/bash
# Auto-generated wrapper for cron
PROJECT_DIR="/home/rezzodan/Рабочий стол/purple-team-lab/purplebot"
VENV_DIR="$PROJECT_DIR/.venv"
SCRIPT="$PROJECT_DIR/ssh_monitor.py"
LOG_FILE="$PROJECT_DIR/monitor.log"

source "$VENV_DIR/bin/activate"
echo "===== $(date '+%Y-%m-%d %H:%M:%S') =====" >> "$LOG_FILE"
python3 "$SCRIPT" >> "$LOG_FILE" 2>&1
echo "" >> "$LOG_FILE"
deactivate
