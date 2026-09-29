#!/usr/bi/env python3
import re
import requests
import sys
from datetime import datetime
from collections import defaultdict

# ===== CONFIGURATION =====
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
LOG_FILE = "/tmp/fake_auth.log"
THRESHOLD = 3           # Alert threshold
ENABLE_GEOIP = True     # Lookup attacker country (free API)
MAX_SOURCES = 10        # Max sources to show in Telegram

# ===== COLORS =====
class C:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'

# ===== GEOIP CACHE =====
_geoip_cache = {}

def get_country(ip):
    """Get country for an IP using free API. Cached."""
    if not ENABLE_GEOIP:
        return "?"
    if ip in _geoip_cache:
        return _geoip_cache[ip]
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=country,countryCode,isp", timeout=3)
        if r.status_code == 200:
            data = r.json()
            if data.get("country"):
                result = f"{data['country']}"
                if data.get('isp'):
                    result += f" / {data['isp']}"
                _geoip_cache[ip] = result
                return result
    except Exception:
        pass
    _geoip_cache[ip] = "Unknown"
    return "Unknown"

def send_telegram(message):
    """Send a message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data, timeout=10)
        if r.status_code == 200:
            print(f"{C.GREEN}[+] Telegram: message sent{C.NC}")
        else:
            print(f"{C.RED}[!] Telegram error: {r.status_code}{C.NC}")
    except Exception as e:
        print(f"{C.RED}[!] Telegram: {e}{C.NC}")

def analyze_ssh_log(log_file):
    """Parse the log and extract detailed info."""
    failed = defaultdict(int)          # user@ip -> count
    users_targeted = defaultdict(int)  # user -> count
    ips_count = defaultdict(int)       # ip -> count
    first_seen = {}                    # user@ip -> timestamp
    last_seen = {}                     # user@ip -> timestamp
    successful = []                    # list of successful logins
    total_failed = 0

    re_failed = re.compile(r'Failed password for (?:invalid user )?(\S+) from (\S+) port \d+')
    re_success = re.compile(r'Accepted (?:password|publickey) for (\S+) from (\S+) port \d+')
    re_time = re.compile(r'^(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})')

    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                time_match = re_time.match(line)
                ts = time_match.group(1) if time_match else "?"

                m = re_failed.search(line)
                if m:
                    user, ip = m.group(1), m.group(2)
                    key = f"{user}@{ip}"
                    failed[key] += 1
                    users_targeted[user] += 1
                    ips_count[ip] += 1
                    total_failed += 1
                    if key not in first_seen:
                        first_seen[key] = ts
                    last_seen[key] = ts
                    continue

                m = re_success.search(line)
                if m:
                    user, ip = m.group(1), m.group(2)
                    successful.append({"time": ts, "user": user, "ip": ip})

    except FileNotFoundError:
        print(f"{C.RED}[!] File {log_file} not found{C.NC}")
        return None
    except PermissionError:
        print(f"{C.RED}[!] Permission denied. Run with sudo.{C.NC}")
        return None

    return {
        "failed": dict(failed),
        "users": dict(users_targeted),
        "ips": dict(ips_count),
        "first_seen": first_seen,
        "last_seen": last_seen,
        "successful": successful,
        "total_failed": total_failed,
    }

def print_report(data):
    """Print a beautiful terminal report."""
    print(f"\n{C.BOLD}{'='*60}{C.NC}")
    print(f"{C.BOLD}  📊 SSH LOG ANALYSIS REPORT{C.NC}")
    print(f"{C.BOLD}{'='*60}{C.NC}")
    print(f"  🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  📁 Log:  {LOG_FILE}")
    print(f"  🎯 Threshold: {THRESHOLD} attempts")

    # Summary
    print(f"\n{C.CYAN}─── SUMMARY ───{C.NC}")
    print(f"  ❌ Total failed attempts:  {C.RED}{data['total_failed']}{C.NC}")
    print(f"  🌐 Unique attacker IPs:    {len(data['ips'])}")
    print(f"  👤 Unique users targeted:  {len(data['users'])}")
    print(f"  ✅ Successful logins:      {C.GREEN}{len(data['successful'])}{C.NC}")

    # All sources
    if data['failed']:
        print(f"\n{C.CYAN}─── ALL SOURCES ───{C.NC}")
        sorted_sources = sorted(data['failed'].items(), key=lambda x: x[1], reverse=True)
        for key, count in sorted_sources[:MAX_SOURCES]:
            marker = f"{C.RED}🚨{C.NC}" if count >= THRESHOLD else f"{C.YELLOW}⚠️ {C.NC}"
            bar = "█" * min(count, 20)
            print(f"  {marker} {key:<30} {bar} {C.BOLD}{count}{C.NC}")

    # Top IPs with GeoIP
    if data['ips']:
        print(f"\n{C.CYAN}─── TOP ATTACKER IPs ───{C.NC}")
        sorted_ips = sorted(data['ips'].items(), key=lambda x: x[1], reverse=True)[:5]
        for ip, count in sorted_ips:
            country = get_country(ip)
            print(f"  {C.RED}{ip:<16}{C.NC} {C.BOLD}{count:>4}{C.NC}  {C.YELLOW}{country}{C.NC}")

    # Users targeted
    if data['users']:
        print(f"\n{C.CYAN}─── USERS TARGETED ───{C.NC}")
        sorted_users = sorted(data['users'].items(), key=lambda x: x[1], reverse=True)[:10]
        for user, count in sorted_users:
            print(f"  {C.MAGENTA}{user:<20}{C.NC} {count} attempts")

    # Suspicious sources with timeline
    suspicious = {k: v for k, v in data['failed'].items() if v >= THRESHOLD}
    if suspicious:
        print(f"\n{C.CYAN}─── 🚨 SUSPICIOUS SOURCES ───{C.NC}")
        for key, count in sorted(suspicious.items(), key=lambda x: x[1], reverse=True):
            first = data['first_seen'].get(key, "?")
            last = data['last_seen'].get(key, "?")
            print(f"  {C.RED}{key}{C.NC}")
            print(f"    Count:   {C.BOLD}{count}{C.NC} attempts")
            print(f"    First:   {first}")
            print(f"    Last:    {last}")

    # Successful logins
    if data['successful']:
        print(f"\n{C.CYAN}─── ✅ RECENT SUCCESSFUL LOGINS ───{C.NC}")
        for s in data['successful'][-10:]:
            print(f"  {C.GREEN}✅{C.NC} {s['time']}  {s['user']}@{s['ip']}")

    print(f"\n{C.BOLD}{'='*60}{C.NC}\n")

def build_telegram_message(data):
    """Build a rich HTML message for Telegram."""
    if data['total_failed'] == 0:
        return None

    msg = "<b>🚨 SSH ACTIVITY REPORT</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Summary
    msg += "<b>📊 Summary</b>\n"
    msg += f"❌ Failed attempts: <b>{data['total_failed']}</b>\n"
    msg += f"🌐 Unique IPs: <b>{len(data['ips'])}</b>\n"
    msg += f"👤 Users targeted: <b>{len(data['users'])}</b>\n"
    msg += f"✅ Successful logins: <b>{len(data['successful'])}</b>\n\n"

    # All sources
    if data['failed']:
        msg += "<b>📋 All Sources</b>\n"
        sorted_sources = sorted(data['failed'].items(), key=lambda x: x[1], reverse=True)[:MAX_SOURCES]
        for key, count in sorted_sources:
            marker = "🚨" if count >= THRESHOLD else "⚠️"
            msg += f"{marker} <code>{key}</code> — <b>{count}</b>\n"
        msg += "\n"

    # Top IPs with GeoIP
    if data['ips']:
        msg += "<b>🎯 Top Attacker IPs</b>\n"
        sorted_ips = sorted(data['ips'].items(), key=lambda x: x[1], reverse=True)[:5]
        for ip, count in sorted_ips:
            country = get_country(ip)
            msg += f"• <code>{ip}</code> — <b>{count}</b> ({country})\n"
        msg += "\n"

    # Users targeted
    if data['users']:
        msg += "<b>👤 Users Targeted</b>\n"
        sorted_users = sorted(data['users'].items(), key=lambda x: x[1], reverse=True)[:5]
        for user, count in sorted_users:
            msg += f"• <code>{user}</code> — {count}\n"
        msg += "\n"

    # Suspicious with timeline
    suspicious = {k: v for k, v in data['failed'].items() if v >= THRESHOLD}
    if suspicious:
        msg += "<b>🚨 Suspicious Sources</b>\n"
        for key, count in sorted(suspicious.items(), key=lambda x: x[1], reverse=True)[:5]:
            first = data['first_seen'].get(key, "?")
            last = data['last_seen'].get(key, "?")
            msg += f"• <code>{key}</code> — <b>{count}</b>\n"
            msg += f"  └ {first} → {last}\n"
        msg += "\n"

    # Successful logins
    if data['successful']:
        msg += "<b>✅ Recent Successful Logins</b>\n"
        for s in data['successful'][-5:]:
            msg += f"• {s['time']} — <code>{s['user']}@{s['ip']}</code>\n"

    return msg

def main():
    print(f"\n{C.BOLD}{C.BLUE}{'='*60}{C.NC}")
    print(f"{C.BOLD}  🛡️  SSH LOG MONITOR — Purple Team{C.NC}")
    print(f"{C.BOLD}{C.BLUE}{'='*60}{C.NC}")

    data = analyze_ssh_log(LOG_FILE)
    if data is None:
        sys.exit(1)

    print_report(data)

    msg = build_telegram_message(data)
    if msg:
        send_telegram(msg)
    else:
        print(f"{C.GREEN}[+] No suspicious activity detected{C.NC}\n")

if __name__ == "__main__":
    main()
