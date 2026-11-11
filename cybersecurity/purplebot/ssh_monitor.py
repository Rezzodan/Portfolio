#!/usr/bin/env python3
"""SSH brute-force monitor: parses an auth log, prints a report and alerts to Telegram."""

import html
import ipaddress
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent

# ===== CONFIGURATION =====
# Values come from environment variables, then from .env next to this script, then from these defaults.
DEFAULTS = {
    "TELEGRAM_TOKEN": "",
    "TELEGRAM_CHAT_ID": "",
    "LOG_FILE": "/var/log/auth.log",
    "THRESHOLD": "5",          # Alert threshold
    "ENABLE_GEOIP": "true",    # Lookup attacker country (free API)
    "MAX_SOURCES": "10",       # Max sources to show in reports
}

RE_FAILED = re.compile(r'Failed password for (?:invalid user )?(\S+) from (\S+) port \d+')
RE_SUCCESS = re.compile(r'Accepted (?:password|publickey) for (\S+) from (\S+) port \d+')
RE_TIME = re.compile(r'^(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})')


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


def read_env_file(path):
    """Parse KEY=VALUE lines from a .env file. Missing file -> empty dict."""
    values = {}
    path = Path(path)
    if not path.is_file():
        return values
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_config(env_file=BASE_DIR / '.env', environ=None):
    environ = os.environ if environ is None else environ
    from_file = read_env_file(env_file)
    raw = {key: environ.get(key, from_file.get(key, default)) for key, default in DEFAULTS.items()}

    token = raw["TELEGRAM_TOKEN"]
    chat_id = raw["TELEGRAM_CHAT_ID"]
    # Placeholders from .env.example count as "not configured".
    telegram_ready = bool(token and chat_id) and not token.startswith("YOUR_") and not chat_id.startswith("YOUR_")

    return {
        "telegram_token": token,
        "telegram_chat_id": chat_id,
        "telegram_enabled": telegram_ready,
        "log_file": raw["LOG_FILE"],
        "threshold": int(raw["THRESHOLD"]),
        "enable_geoip": raw["ENABLE_GEOIP"].strip().lower() in ("1", "true", "yes"),
        "max_sources": int(raw["MAX_SOURCES"]),
    }


# ===== GEOIP CACHE =====
_geoip_cache = {}


def get_country(ip, enabled=True):
    """Get country for an IP using free API. Cached. Private addresses are never sent out."""
    if not enabled:
        return "?"
    try:
        if not ipaddress.ip_address(ip).is_global:
            return "Private network"
    except ValueError:
        return "Unknown"
    if ip in _geoip_cache:
        return _geoip_cache[ip]
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", params={"fields": "country,isp"}, timeout=3)
        if r.status_code == 200:
            data = r.json()
            if data.get("country"):
                result = data["country"]
                if data.get("isp"):
                    result += f" / {data['isp']}"
                _geoip_cache[ip] = result
                return result
    except requests.RequestException:
        pass
    _geoip_cache[ip] = "Unknown"
    return "Unknown"


def send_telegram(message, config):
    """Send a message to Telegram. Returns True on success."""
    if not config["telegram_enabled"]:
        print(f"{C.YELLOW}[!] Telegram not configured (TELEGRAM_TOKEN / TELEGRAM_CHAT_ID), skipping alert{C.NC}")
        return False
    url = f"https://api.telegram.org/bot{config['telegram_token']}/sendMessage"
    data = {"chat_id": config["telegram_chat_id"], "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data, timeout=10)
    except requests.RequestException as e:
        print(f"{C.RED}[!] Telegram: {e.__class__.__name__}{C.NC}")
        return False
    if r.status_code == 200:
        print(f"{C.GREEN}[+] Telegram: message sent{C.NC}")
        return True
    print(f"{C.RED}[!] Telegram error: {r.status_code}{C.NC}")
    return False


def parse_log_lines(lines):
    """Extract failed and successful SSH logins from auth log lines."""
    failed = defaultdict(int)          # user@ip -> count
    users_targeted = defaultdict(int)  # user -> count
    ips_count = defaultdict(int)       # ip -> count
    first_seen = {}                    # user@ip -> timestamp
    last_seen = {}                     # user@ip -> timestamp
    successful = []                    # list of successful logins
    total_failed = 0

    for line in lines:
        time_match = RE_TIME.match(line)
        ts = time_match.group(1) if time_match else "?"

        m = RE_FAILED.search(line)
        if m:
            user, ip = m.group(1), m.group(2)
            key = f"{user}@{ip}"
            failed[key] += 1
            users_targeted[user] += 1
            ips_count[ip] += 1
            total_failed += 1
            first_seen.setdefault(key, ts)
            last_seen[key] = ts
            continue

        m = RE_SUCCESS.search(line)
        if m:
            successful.append({"time": ts, "user": m.group(1), "ip": m.group(2)})

    return {
        "failed": dict(failed),
        "users": dict(users_targeted),
        "ips": dict(ips_count),
        "first_seen": first_seen,
        "last_seen": last_seen,
        "successful": successful,
        "total_failed": total_failed,
    }


def analyze_ssh_log(log_file):
    """Read the log file and parse it. Returns None if the file can't be read."""
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            return parse_log_lines(f)
    except FileNotFoundError:
        print(f"{C.RED}[!] File {log_file} not found{C.NC}")
    except PermissionError:
        print(f"{C.RED}[!] Permission denied. Run with sudo.{C.NC}")
    return None


def suspicious_sources(data, threshold):
    return {k: v for k, v in data['failed'].items() if v >= threshold}


def top(counter, limit):
    return sorted(counter.items(), key=lambda x: x[1], reverse=True)[:limit]


def print_report(data, config):
    """Print a terminal report."""
    threshold = config["threshold"]
    print(f"\n{C.BOLD}{'='*60}{C.NC}")
    print(f"{C.BOLD}  📊 SSH LOG ANALYSIS REPORT{C.NC}")
    print(f"{C.BOLD}{'='*60}{C.NC}")
    print(f"  🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  📁 Log:  {config['log_file']}")
    print(f"  🎯 Threshold: {threshold} attempts")

    print(f"\n{C.CYAN}─── SUMMARY ───{C.NC}")
    print(f"  ❌ Total failed attempts:  {C.RED}{data['total_failed']}{C.NC}")
    print(f"  🌐 Unique attacker IPs:    {len(data['ips'])}")
    print(f"  👤 Unique users targeted:  {len(data['users'])}")
    print(f"  ✅ Successful logins:      {C.GREEN}{len(data['successful'])}{C.NC}")

    if data['failed']:
        print(f"\n{C.CYAN}─── ALL SOURCES ───{C.NC}")
        for key, count in top(data['failed'], config["max_sources"]):
            marker = f"{C.RED}🚨{C.NC}" if count >= threshold else f"{C.YELLOW}⚠️ {C.NC}"
            bar = "█" * min(count, 20)
            print(f"  {marker} {key:<30} {bar} {C.BOLD}{count}{C.NC}")

    if data['ips']:
        print(f"\n{C.CYAN}─── TOP ATTACKER IPs ───{C.NC}")
        for ip, count in top(data['ips'], 5):
            country = get_country(ip, config["enable_geoip"])
            print(f"  {C.RED}{ip:<16}{C.NC} {C.BOLD}{count:>4}{C.NC}  {C.YELLOW}{country}{C.NC}")

    if data['users']:
        print(f"\n{C.CYAN}─── USERS TARGETED ───{C.NC}")
        for user, count in top(data['users'], 10):
            print(f"  {C.MAGENTA}{user:<20}{C.NC} {count} attempts")

    suspicious = suspicious_sources(data, threshold)
    if suspicious:
        print(f"\n{C.CYAN}─── 🚨 SUSPICIOUS SOURCES ───{C.NC}")
        for key, count in top(suspicious, len(suspicious)):
            print(f"  {C.RED}{key}{C.NC}")
            print(f"    Count:   {C.BOLD}{count}{C.NC} attempts")
            print(f"    First:   {data['first_seen'].get(key, '?')}")
            print(f"    Last:    {data['last_seen'].get(key, '?')}")

    if data['successful']:
        print(f"\n{C.CYAN}─── ✅ RECENT SUCCESSFUL LOGINS ───{C.NC}")
        for s in data['successful'][-10:]:
            print(f"  {C.GREEN}✅{C.NC} {s['time']}  {s['user']}@{s['ip']}")

    print(f"\n{C.BOLD}{'='*60}{C.NC}\n")


def build_telegram_message(data, config):
    """Build an HTML message for Telegram. Log values are escaped: usernames come from attackers."""
    if data['total_failed'] == 0:
        return None

    e = html.escape
    threshold = config["threshold"]

    msg = "<b>🚨 SSH ACTIVITY REPORT</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    msg += "<b>📊 Summary</b>\n"
    msg += f"❌ Failed attempts: <b>{data['total_failed']}</b>\n"
    msg += f"🌐 Unique IPs: <b>{len(data['ips'])}</b>\n"
    msg += f"👤 Users targeted: <b>{len(data['users'])}</b>\n"
    msg += f"✅ Successful logins: <b>{len(data['successful'])}</b>\n\n"

    if data['failed']:
        msg += "<b>📋 All Sources</b>\n"
        for key, count in top(data['failed'], config["max_sources"]):
            marker = "🚨" if count >= threshold else "⚠️"
            msg += f"{marker} <code>{e(key)}</code> — <b>{count}</b>\n"
        msg += "\n"

    if data['ips']:
        msg += "<b>🎯 Top Attacker IPs</b>\n"
        for ip, count in top(data['ips'], 5):
            country = get_country(ip, config["enable_geoip"])
            msg += f"• <code>{e(ip)}</code> — <b>{count}</b> ({e(country)})\n"
        msg += "\n"

    if data['users']:
        msg += "<b>👤 Users Targeted</b>\n"
        for user, count in top(data['users'], 5):
            msg += f"• <code>{e(user)}</code> — {count}\n"
        msg += "\n"

    suspicious = suspicious_sources(data, threshold)
    if suspicious:
        msg += "<b>🚨 Suspicious Sources</b>\n"
        for key, count in top(suspicious, 5):
            first = data['first_seen'].get(key, "?")
            last = data['last_seen'].get(key, "?")
            msg += f"• <code>{e(key)}</code> — <b>{count}</b>\n"
            msg += f"  └ {e(first)} → {e(last)}\n"
        msg += "\n"

    if data['successful']:
        msg += "<b>✅ Recent Successful Logins</b>\n"
        for s in data['successful'][-5:]:
            msg += f"• {e(s['time'])} — <code>{e(s['user'])}@{e(s['ip'])}</code>\n"

    return msg


def main():
    config = load_config()

    print(f"\n{C.BOLD}{C.BLUE}{'='*60}{C.NC}")
    print(f"{C.BOLD}  🛡️  SSH LOG MONITOR — Purple Team{C.NC}")
    print(f"{C.BOLD}{C.BLUE}{'='*60}{C.NC}")

    data = analyze_ssh_log(config["log_file"])
    if data is None:
        sys.exit(1)

    print_report(data, config)

    msg = build_telegram_message(data, config)
    if msg:
        send_telegram(msg, config)
    else:
        print(f"{C.GREEN}[+] No suspicious activity detected{C.NC}\n")


if __name__ == "__main__":
    main()
