# 🛡️ Purple Team Bot — SSH Attack Monitor

A real-time SSH log monitor that detects brute-force attacks and sends instant alerts to Telegram.

Built as part of my **Purple Team Security Engineer** roadmap — combining offensive knowledge (how attacks look) with defensive automation (how to detect them).

---

## 🎯 Overview

This tool continuously analyzes SSH authentication logs, identifies suspicious patterns (multiple failed login attempts), and notifies the security analyst via Telegram in real time.

**Use case:** SOC Analyst / Blue Team Engineer needs immediate visibility into brute-force attempts against production servers.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3 |
| HTTP Client | `requests` |
| Log Parsing | `re` (regex) |
| Notifications | Telegram Bot API |
| Environment | `venv` (isolated) |
| OS | Kali Linux |
| Scheduling | cron |

---

## 📐 Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  SSH Log File   │────▶│  ssh_monitor.py  │────▶│  Telegram Bot   │
│ (/var/log/auth) │     │  (regex parser)  │     │  (alert to SOC) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## 🚀 Features

- ✅ Parses SSH authentication logs
- ✅ Detects failed login attempts (`Failed password`)
- ✅ Counts attempts per user/IP
- ✅ Tracks first/last seen timestamps
- ✅ GeoIP lookup for attacker IPs (country + ISP)
- ✅ Detects successful logins (audit trail)
- ✅ Sends alerts to Telegram when threshold is exceeded
- ✅ Configurable alert threshold
- ✅ Colored terminal output with bar charts
- ✅ Automated installation script (`install.sh`)
- ✅ Cron scheduling with custom intervals
- ✅ Runs in isolated `venv` environment

---

## 📋 Installation

### 🚀 Quick Start (Automated)

**One command to rule them all:**

```bash
git clone https://github.com/Rezzodan/purple-team-lab.git
cd purple-team-lab/purplebot
sudo ./install.sh
```

The installer will:
1. ✅ Check Python and dependencies
2. ✅ Create virtual environment
3. ✅ Ask for your Telegram token and chat ID
4. ✅ Configure the monitor
5. ✅ Set up cron job (choose your interval)
6. ✅ Send a test message to Telegram
7. ✅ Run the first scan

**That's it!** The monitor is now running 24/7.

---

### 🛠️ Manual Installation

#### 1. Clone the repository
```bash
git clone https://github.com/Rezzodan/purple-team-lab.git
cd purple-team-lab/purplebot
```

#### 2. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install dependencies
```bash
pip install --upgrade pip
pip install requests
```

#### 4. Configure Telegram Bot
1. Find **@BotFather** in Telegram
2. Send `/newbot` and follow instructions
3. Save the **token** (e.g. `1234567890:ABCdef...`)
4. Find **@userinfobot** to get your **chat_id**
5. Send `/start` to your bot (otherwise it can't message you)

#### 5. Edit configuration

Open `ssh_monitor.py` and set:

```python
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
LOG_FILE = "/var/log/auth.log"
THRESHOLD = 5
```

---

## 🎮 Usage

### Run the monitor manually
```bash
sudo python3 ssh_monitor.py
```

### Expected output
```
============================================================
  📊 SSH LOG ANALYSIS REPORT
============================================================
  🕐 Time: 2026-09-14 13:43:35
  📁 Log:  /tmp/fake_auth.log
  🎯 Threshold: 3 attempts

─── SUMMARY ───
  ❌ Total failed attempts:  8
  🌐 Unique attacker IPs:    2
  👤 Unique users targeted:  2
  ✅ Successful logins:      0

─── ALL SOURCES ───
  🚨 root@192.168.1.100             █████ 5
  🚨 admin@10.0.0.50                ███ 3

─── TOP ATTACKER IPs ───
  192.168.1.100       5  Unknown
  10.0.0.50           3  Unknown

─── USERS TARGETED ───
  root                 5 attempts
  admin                3 attempts

─── 🚨 SUSPICIOUS SOURCES ───
  root@192.168.1.100
    Count:   5 attempts
    First:   Sep 14 10:00:01
    Last:    Sep 14 10:00:05

============================================================
[+] Telegram: message sent
```

### Telegram alert
```
🚨 SSH ACTIVITY REPORT
━━━━━━━━━━━━━━━━━━━━
📅 Time: 2026-09-14 13:43:35

📊 Summary
❌ Failed attempts: 8
🌐 Unique IPs: 2
👤 Users targeted: 2
✅ Successful logins: 0

📋 All Sources
🚨 root@192.168.1.100 — 5
🚨 admin@10.0.0.50 — 3

🎯 Top Attacker IPs
• 192.168.1.100 — 5 (Unknown)
• 10.0.0.50 — 3 (Unknown)

🚨 Suspicious Sources
• root@192.168.1.100 — 5
  └ Sep 14 10:00:01 → Sep 14 10:00:05
```

---

## ⏰ Cron Schedule

During installation, you can choose how often the monitor runs:

| Option | Schedule | Use Case |
|--------|----------|----------|
| 1 | Every 5 minutes | High security, more API calls |
| 2 | Every 15 minutes | Balanced |
| 3 | Every 30 minutes | Light |
| 4 | Every hour | Low |
| 5 | Every 5 hours | Very low |
| 6 | Custom | Your own schedule |

### Change Schedule Later

**Option A:** Re-run the installer
```bash
sudo ./install.sh
```
The installer will detect and replace the old cron job.

**Option B:** Edit manually
```bash
sudo crontab -e
```

**Cron format:**
```
minute hour day month weekday command
  *     *    *    *      *
```

**Examples:**
- `*/5 * * * *` — every 5 minutes
- `0 */5 * * *` — every 5 hours
- `0 9 * * *` — every day at 09:00
- `0 0 * * 1` — every Monday at midnight

---

## 🧪 Testing

A sample log file is included for safe testing:

```bash
# Create fake log
cat > /tmp/fake_auth.log << 'LOGEOF'
Sep 14 10:00:01 kali sshd[1234]: Failed password for root from 192.168.1.100 port 12345 ssh2
Sep 14 10:00:02 kali sshd[1234]: Failed password for root from 192.168.1.100 port 12346 ssh2
Sep 14 10:00:03 kali sshd[1234]: Failed password for root from 192.168.1.100 port 12347 ssh2
Sep 14 10:00:04 kali sshd[1234]: Failed password for root from 192.168.1.100 port 12348 ssh2
Sep 14 10:00:05 kali sshd[1234]: Failed password for root from 192.168.1.100 port 12349 ssh2
Sep 14 10:00:06 kali sshd[1234]: Failed password for admin from 10.0.0.50 port 54321 ssh2
Sep 14 10:00:07 kali sshd[1234]: Failed password for admin from 10.0.0.50 port 54322 ssh2
Sep 14 10:00:08 kali sshd[1234]: Failed password for admin from 10.0.0.50 port 54323 ssh2
Sep 14 10:00:09 kali sshd[1234]: Accepted password for rezzodan from 192.168.1.50 port 12345 ssh2
LOGEOF

# Run monitor against fake log
sudo python3 ssh_monitor.py
```

---

## 🔍 How It Works

### 1. Log Parsing
The script reads the log file line by line and uses regex to extract:
- Username
- Source IP
- Failed password event
- Timestamp

```python
match = re.search(r'Failed password for (?:invalid user )?(\S+) from (\S+)', line)
```

### 2. Aggregation
Failed attempts are counted per `user@ip` pair:
```python
failed_attempts[key] = failed_attempts.get(key, 0) + 1
```

### 3. GeoIP Enrichment
Each attacker IP is enriched with country and ISP via `ip-api.com`:
```python
r = requests.get(f"http://ip-api.com/json/{ip}?fields=country,isp", timeout=3)
```

### 4. Alerting
If any source exceeds the threshold (`THRESHOLD`), an alert is sent to Telegram via HTTP API.

---

## 🛡️ Purple Team Perspective

### 🔴 Red Team View
- Brute-force attacks leave a clear pattern in logs
- Multiple `Failed password` entries from the same IP = detectable
- Attackers often use common usernames (`root`, `admin`, `test`)

### 🔵 Blue Team View
- Real-time log monitoring is critical
- Automated alerting reduces response time
- Threshold-based detection catches brute-force early
- GeoIP enrichment helps prioritize threats

---

## 📁 Project Structure

```
purplebot/
├── .venv/                  # Virtual environment (not committed)
├── install.sh              # Automated installer
├── run_monitor.sh          # Wrapper script for cron
├── ssh_monitor.py          # Main SSH monitor script
├── test_bot.py             # Telegram bot connectivity test
├── monitor.log             # Output log from cron runs
├── README.md               # This file
└── requirements.txt        # Dependencies
```

---

## 🔮 Future Improvements

- [ ] Parse `journald` instead of file (for Kali/systemd)
- [ ] Add IP geolocation caching to disk
- [ ] Integrate with Wazuh SIEM
- [ ] Add support for multiple log sources
- [ ] Add web dashboard (Flask + Chart.js)
- [ ] Add email notifications as fallback
- [ ] Add fail2ban integration (auto-block IPs)
- [ ] Docker container for easy deployment

---

## 📬 Connect

- **Telegram:** [@rezzodan](https://t.me/rezzodan)
- **GitHub:** [Rezzodan](https://github.com/Rezzodan)
- **Email:** malooyy6@gmail.com

---

## 📄 License

This project is for educational and portfolio purposes only.
All testing was performed in isolated lab environments.

