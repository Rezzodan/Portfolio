#!/usr/bin/env python3
import requests

# ===== НАСТРОЙКИ =====
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print("[+] Сообщение отправлено!")
        else:
            print(f"[!] Ошибка: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[!] Ошибка: {e}")

if __name__ == "__main__":
    send_telegram("🧪 <b>test bot!</b>\nIf you see this, everything works!")
