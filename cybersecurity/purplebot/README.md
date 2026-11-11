# 🛡️ Purple Team Bot — SSH Brute-Force Monitor

[![purplebot](https://github.com/Rezzodan/Portfolio/actions/workflows/purplebot.yml/badge.svg)](https://github.com/Rezzodan/Portfolio/actions/workflows/purplebot.yml)

A Python tool that parses SSH authentication logs, flags brute-force sources above a threshold, enriches attacker
IPs with GeoIP data and sends an alert to Telegram. Runs on a schedule via cron.

**Use case:** a small team without a SIEM still gets immediate visibility into password-guessing against its servers.

<img src="telegram-alert.png" alt="Telegram alert produced by the bot" width="320">

## Architecture

```text
┌──────────────────┐     ┌────────────────────────┐     ┌──────────────────┐
│ /var/log/auth.log│────▶│ ssh_monitor.py         │────▶│ Telegram Bot API │
│ (sshd events)    │     │ parse → aggregate →    │     │ alert to analyst │
└──────────────────┘     │ threshold → enrich     │     └──────────────────┘
        cron ───────────▶└────────────────────────┘
```

## Features

- Detects `Failed password` events, including `invalid user` attempts, and counts them per `user@ip`
- Tracks first / last seen time for every source and highlights sources above the threshold
- Lists successful logins next to the failures as an audit trail
- GeoIP enrichment (country, ISP) with an in-memory cache
- Colored terminal report and an HTML Telegram summary
- Interactive installer: virtualenv, config, cron schedule, test message

## Security design

The bot handles a secret (the Telegram token) and untrusted input (usernames typed by attackers), so:

| Risk | Mitigation |
|------|------------|
| Token committed to Git or visible in the process list | Config lives in `.env` (git-ignored, `chmod 600`); the installer reads the token with hidden input and never passes it on a command line |
| Token leaking through error messages (it is part of the API URL) | Network errors are logged by exception type only |
| Attacker-controlled usernames breaking or spoofing the HTML alert | All log values are HTML-escaped before sending — covered by a test |
| Internal addresses leaking to a third-party API | Private / reserved IPs are never sent to the GeoIP service |
| Alerts silently going to a placeholder bot | Placeholder values from `.env.example` disable Telegram with a warning |

## Quick start

```bash
git clone https://github.com/Rezzodan/Portfolio.git
cd Portfolio/cybersecurity/purplebot
sudo ./install.sh
```

The installer checks Python, creates `.venv`, asks for the Telegram token, chat id, log path and threshold, writes
`.env`, sets up the cron job, sends a test message and runs the first scan.

### Manual setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && chmod 600 .env   # fill in TELEGRAM_TOKEN and TELEGRAM_CHAT_ID
python3 send_test_message.py             # check Telegram settings
sudo .venv/bin/python3 ssh_monitor.py
```

Get a token from **@BotFather**, your chat id from **@userinfobot**, and send `/start` to your bot first.

### Configuration

| Variable | Default | Meaning |
|----------|---------|---------|
| `TELEGRAM_TOKEN` | — | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | — | Where alerts are sent |
| `LOG_FILE` | `/var/log/auth.log` | SSH log to analyze |
| `THRESHOLD` | `5` | Failed attempts per `user@ip` that mark a source as suspicious |
| `ENABLE_GEOIP` | `true` | Look up country / ISP for public IPs |
| `MAX_SOURCES` | `10` | Sources listed in a report |

Environment variables override values from `.env`.

## Try it on the sample log

```bash
LOG_FILE=tests/fixtures/auth.log ENABLE_GEOIP=false python3 ssh_monitor.py
```

```text
─── SUMMARY ───
  ❌ Total failed attempts:  8
  🌐 Unique attacker IPs:    2
  👤 Unique users targeted:  3
  ✅ Successful logins:      1

─── ALL SOURCES ───
  🚨 root@203.0.113.10              █████ 5
  ⚠️  admin@198.51.100.7             ██ 2
  ⚠️  <b>x</b>@198.51.100.7          █ 1
```

The `<b>x</b>` username is a deliberate injection attempt in the fixture: it is printed as text and escaped in the
Telegram message.

## Tests and CI

```bash
pip install pytest ruff
ruff check .   # includes bandit (S) security rules
pytest -q      # 12 tests: parsing, threshold, escaping, config, no GeoIP for private IPs
```

GitHub Actions runs both on every change to this folder.

## Known limitations and next steps

- The threshold counts attempts over the whole log, not within a time window — next: sliding window per source
- Each run re-reads the full log, so the same activity is reported again — next: remember the last read offset
- Systems without rsyslog keep SSH events only in journald — next: read from `journalctl -u ssh`
- Cron runs the monitor as root — it only needs read access, so a dedicated user in the `adm` group is better
- Response is manual — next: optional fail2ban / firewall block for sources above the threshold

## Project structure

```text
purplebot/
├── ssh_monitor.py          # parser, report, Telegram alert
├── send_test_message.py    # checks Telegram settings
├── install.sh              # interactive installer + cron
├── requirements.txt
├── pyproject.toml          # pytest and ruff settings
├── .env.example            # config template (real .env is git-ignored)
└── tests/
    ├── fixtures/auth.log   # sample sshd log
    └── test_ssh_monitor.py
```

## Related

- [SIEM with Wazuh](../SIEM/)
- [Network IDS with Suricata](../ids-suricata/)

All testing was performed in an isolated lab environment.
