#!/bin/bash
# ============================================================
#  Purple Team Bot — Automated Installer
#  SSH Attack Monitor with Telegram Alerts
# ============================================================

set -e  # Exit on error

# ===== COLORS =====
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ===== BANNER =====
clear
echo -e "${BLUE}"
echo "============================================================"
echo "   🛡️  Purple Team Bot — SSH Attack Monitor"
echo "   Automated Installer v2.0"
echo "============================================================"
echo -e "${NC}"

# ===== CHECK ROOT =====
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[!] Please run as root: sudo ./install.sh${NC}"
    exit 1
fi

# ===== CHECK PYTHON =====
echo -e "${YELLOW}[*] Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python 3 not found. Install it first:${NC}"
    echo "    sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
echo -e "${GREEN}[+] Python 3 found: $(python3 --version)${NC}"

# ===== CHECK VENV MODULE =====
echo -e "${YELLOW}[*] Checking venv module...${NC}"
if ! python3 -m venv --help &> /dev/null; then
    echo -e "${RED}[!] venv module not found. Install it:${NC}"
    echo "    sudo apt install python3-venv"
    exit 1
fi
echo -e "${GREEN}[+] venv module available${NC}"

# ===== PROJECT DIRECTORY =====
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "${YELLOW}[*] Project directory: ${PROJECT_DIR}${NC}"

# ===== CREATE VENV =====
echo -e "${YELLOW}[*] Creating virtual environment...${NC}"
if [ -d "$PROJECT_DIR/.venv" ]; then
    echo -e "${YELLOW}[!] .venv already exists, skipping${NC}"
else
    python3 -m venv "$PROJECT_DIR/.venv"
    echo -e "${GREEN}[+] .venv created${NC}"
fi

# ===== INSTALL DEPENDENCIES =====
echo -e "${YELLOW}[*] Installing dependencies...${NC}"
"$PROJECT_DIR/.venv/bin/pip" install --upgrade pip --quiet
"$PROJECT_DIR/.venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt" --quiet
echo -e "${GREEN}[+] Dependencies installed${NC}"

# ===== TELEGRAM SETUP =====
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}   Telegram Bot Setup${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo "Before continuing, make sure you have:"
echo "  1. Created a bot via @BotFather in Telegram"
echo "  2. Got your chat_id via @userinfobot"
echo "  3. Sent /start to your bot"
echo ""
read -p "Press ENTER to continue..."

echo ""
read -s -p "Enter your Telegram BOT TOKEN (input hidden): " TELEGRAM_TOKEN
echo ""
if [ -z "$TELEGRAM_TOKEN" ]; then
    echo -e "${RED}[!] Token cannot be empty${NC}"
    exit 1
fi

echo ""
read -p "Enter your Telegram CHAT ID: " TELEGRAM_CHAT_ID
if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo -e "${RED}[!] Chat ID cannot be empty${NC}"
    exit 1
fi

# ===== MONITOR SETTINGS =====
echo ""
read -p "Auth log to monitor [/var/log/auth.log]: " LOG_SOURCE
LOG_SOURCE="${LOG_SOURCE:-/var/log/auth.log}"
if [ ! -f "$LOG_SOURCE" ]; then
    echo -e "${YELLOW}[!] $LOG_SOURCE not found. On systems without rsyslog: sudo apt install rsyslog${NC}"
fi

read -p "Alert threshold, failed attempts per source [5]: " THRESHOLD
THRESHOLD="${THRESHOLD:-5}"
if ! [[ "$THRESHOLD" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}[!] Threshold must be a number${NC}"
    exit 1
fi

# ===== WRITE .env =====
echo -e "${YELLOW}[*] Writing configuration to .env...${NC}"
ENV_FILE="$PROJECT_DIR/.env"
(
    umask 077
    cat > "$ENV_FILE" << EOF
TELEGRAM_TOKEN=$TELEGRAM_TOKEN
TELEGRAM_CHAT_ID=$TELEGRAM_CHAT_ID
LOG_FILE=$LOG_SOURCE
THRESHOLD=$THRESHOLD
EOF
)
chmod 600 "$ENV_FILE"
echo -e "${GREEN}[+] Saved $ENV_FILE (readable by owner only)${NC}"

# ===== CREATE WRAPPER SCRIPT =====
echo -e "${YELLOW}[*] Creating wrapper script...${NC}"
WRAPPER="$PROJECT_DIR/run_monitor.sh"

cat > "$WRAPPER" << EOF
#!/bin/bash
# Auto-generated wrapper for cron
PROJECT_DIR="$PROJECT_DIR"
VENV_DIR="\$PROJECT_DIR/.venv"
SCRIPT="\$PROJECT_DIR/ssh_monitor.py"
LOG_FILE="\$PROJECT_DIR/monitor.log"

source "\$VENV_DIR/bin/activate"
echo "===== \$(date '+%Y-%m-%d %H:%M:%S') =====" >> "\$LOG_FILE"
python3 "\$SCRIPT" >> "\$LOG_FILE" 2>&1
echo "" >> "\$LOG_FILE"
deactivate
EOF

chmod +x "$WRAPPER"
echo -e "${GREEN}[+] Wrapper script created: $WRAPPER${NC}"

# ===== SETUP CRON =====
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}   Cron Schedule Setup${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo "How often should the monitor run?"
echo ""
echo "  1) Every 5 minutes   (high security, more API calls)"
echo "  2) Every 15 minutes  (balanced)"
echo "  3) Every 30 minutes  (light)"
echo "  4) Every hour        (low)"
echo "  5) Every 5 hours     (very low)"
echo "  6) Custom            (enter your own)"
echo ""
read -p "Choose [1-6] (default: 1): " CRON_CHOICE

case "$CRON_CHOICE" in
    2) CRON_SCHEDULE="*/15 * * * *" ; CRON_DESC="every 15 minutes" ;;
    3) CRON_SCHEDULE="*/30 * * * *" ; CRON_DESC="every 30 minutes" ;;
    4) CRON_SCHEDULE="0 * * * *"    ; CRON_DESC="every hour" ;;
    5) CRON_SCHEDULE="0 */5 * * *"  ; CRON_DESC="every 5 hours" ;;
    6)
        echo ""
        echo "Enter cron schedule (5 fields: min hour day month weekday)"
        echo "Examples:"
        echo "  '*/10 * * * *'  — every 10 minutes"
        echo "  '0 */2 * * *'   — every 2 hours"
        echo "  '0 9 * * *'     — every day at 09:00"
        echo "  '0 0 * * 1'     — every Monday at midnight"
        echo ""
        read -p "Cron schedule: " CRON_SCHEDULE
        CRON_DESC="custom: $CRON_SCHEDULE"
        ;;
    *) CRON_SCHEDULE="*/5 * * * *"  ; CRON_DESC="every 5 minutes" ;;
esac

echo ""
echo -e "${YELLOW}[*] Setting up cron job ($CRON_DESC)...${NC}"

CRON_LINE="$CRON_SCHEDULE \"$WRAPPER\""

# Remove old Purple Team Bot cron jobs (if any)
if crontab -l 2>/dev/null | grep -q "$WRAPPER"; then
    echo -e "${YELLOW}[!] Removing old cron job...${NC}"
    crontab -l 2>/dev/null | grep -v "$WRAPPER" | grep -v "# Purple Team Bot" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "# Purple Team Bot — SSH Monitor"; echo "$CRON_LINE") | crontab -
echo -e "${GREEN}[+] Cron job added: $CRON_DESC${NC}"

# ===== TEST TELEGRAM =====
echo ""
echo -e "${YELLOW}[*] Testing Telegram connection...${NC}"
if ! "$PROJECT_DIR/.venv/bin/python3" "$PROJECT_DIR/send_test_message.py"; then
    echo -e "${YELLOW}[!] Test message failed — check the token and chat id in $ENV_FILE${NC}"
fi

# ===== FIRST RUN =====
echo ""
echo -e "${YELLOW}[*] Running first scan...${NC}"
"$WRAPPER"
echo -e "${GREEN}[+] First scan complete. Check monitor.log${NC}"

# ===== DONE =====
echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}   ✅ Installation Complete!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo "What's next:"
echo "  📄 Logs:        $PROJECT_DIR/monitor.log"
echo "  ⚙️  Config:      $ENV_FILE"
echo "  🔧 Cron:        sudo crontab -l"
echo "  🧪 Manual run:  sudo $WRAPPER"
echo ""
echo "The monitor will run $CRON_DESC automatically."
echo ""
echo -e "${YELLOW}💡 Want to change the schedule later?${NC}"
echo "   Run: sudo ./install.sh   (it will detect existing cron and update)"
echo "   Or:  sudo crontab -e      (edit manually)"
echo ""
echo -e "${BLUE}Stay safe! 🛡️${NC}"
echo ""
