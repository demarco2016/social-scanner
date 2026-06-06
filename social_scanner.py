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
    url = "https://api.coingecko.com/api/v3/news"
    res = requests.get(url)
    if res.status_code == 200:
        news = res.json().get("data", [])[:5]
        return [f"🔥 {n['title']}" for n in news]
    return []

def run():
    print("\nSocial Scanner - Crypto News\n")
    msg = "Social Scanner - Crypto News\n\n"

    print("--- CryptoPanic ---")
    msg += "--- CryptoPanic ---\n"
    for n in get_cryptopanic():
        print(n)
        msg += n + "\n"

    print("\n--- CoinGecko News ---")
    msg += "\n--- CoinGecko News ---\n"
    for n in get_coingecko_news():
        print(n)
        msg += n + "\n"

    send_telegram(msg)

REFRESH_MINUTES = 10

while True:
    run()
    print(f"\nNext check in {REFRESH_MINUTES} min...\n")
    time.sleep(REFRESH_MINUTES * 60)
