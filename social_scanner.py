import requests, os, time
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg[:4096]})

def get_rss(url, source, limit=3):
    try:
        res = requests.get(url, timeout=10)
        root = ET.fromstring(res.content)
        items = root.findall(".//item")[:limit]
        return [f"[{source}] {item.find('title').text}" for item in items]
    except:
        return []

def get_coingecko_news():
    try:
        url = "https://api.coingecko.com/api/v3/news"
        res = requests.get(url, timeout=10)
        news = res.json().get("data", [])[:3]
        return [f"[CoinGecko] {n['title']}" for n in news]
    except:
        return []

def run():
    print("\nSocial Scanner - Crypto News\n")
    msg = "Social Scanner\n\n"
    sources = [
        ("https://cointelegraph.com/rss", "CoinTelegraph"),
        ("https://decrypt.co/feed", "Decrypt"),
    ]
    for url, name in sources:
        news = get_rss(url, name)
        for n in news:
            print(n)
            msg += n + "\n"
    for n in get_coingecko_news():
        print(n)
        msg += n + "\n"
    send_telegram(msg)
    print()

REFRESH_MINUTES = 10

while True:
    run()
    print(f"\nNext check in {REFRESH_MINUTES} min...\n")
    time.sleep(REFRESH_MINUTES * 60)
