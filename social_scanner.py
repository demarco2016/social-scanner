import requests, os, time
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

def get_cryptopanic():
    url = "https://cryptopanic.com/api/v1/posts/?auth_token=pub_free&public=true&kind=news"
    res = requests.get(url)
    if res.status_code == 200:
        posts = res.json().get("results", [])[:5]
        return [f"📰 {p['title']}" for p in posts]
    return []

def get_coingecko_news():
    url = "https:
