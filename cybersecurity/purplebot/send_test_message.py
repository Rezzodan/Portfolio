#!/usr/bin/env python3
"""Send one test message to check the Telegram token and chat id from .env."""

import sys

from ssh_monitor import load_config, send_telegram

if __name__ == "__main__":
    config = load_config()
    ok = send_telegram("🧪 <b>Purple Team Bot</b>\nIf you see this, Telegram alerts work!", config)
    sys.exit(0 if ok else 1)
