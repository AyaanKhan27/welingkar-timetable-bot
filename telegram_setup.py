import os
import requests


TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

response = requests.get(url, timeout=30)

response.raise_for_status()

data = response.json()

print("Telegram API response:")

print(data)
