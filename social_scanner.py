"""Read public RSS feeds and optionally deliver their headlines to Telegram."""
import argparse
import os
import sys
import time
import xml.etree.ElementTree as ET
import requests
from dotenv import load_dotenv

SOURCES = [("https://cointelegraph.com/rss", "CoinTelegraph"),
           ("https://decrypt.co/feed", "Decrypt")]
TIMEOUT = 15
MAX_FEED_BYTES = 2_000_000

class FeedError(Exception):
    pass


def get_rss(url, source, limit=3, session=requests):
    try:
        with session.get(url, timeout=TIMEOUT, stream=True) as response:
            response.raise_for_status()
            chunks = []
            size = 0
            for chunk in response.iter_content(65536):
                size += len(chunk)
                if size > MAX_FEED_BYTES:
                    raise FeedError(f"{source}: feed exceeds size limit")
                chunks.append(chunk)
        content = b"".join(chunks)
        if b"<!DOCTYPE" in content.upper() or b"<!ENTITY" in content.upper():
            raise FeedError(f"{source}: unsupported XML declarations")
        root = ET.fromstring(content)
        if root.tag not in ("rss", "{http://www.w3.org/2005/Atom}feed", "feed"):
            raise FeedError(f"{source}: unsupported feed format")
        entries = root.findall("./channel/item")
        if root.tag != "rss":
            entries = root.findall("{http://www.w3.org/2005/Atom}entry") or root.findall("entry")
        headlines = []
        for item in entries:
            title = item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title")
            if title and title.strip():
                headlines.append(f"[{source}] {' '.join(title.split())}")
            if len(headlines) >= limit:
                break
        return headlines
    except (requests.RequestException, ET.ParseError) as error:
        # Exception URLs may contain credentials. Do not expose them.
        raise FeedError(f"{source}: feed unavailable or invalid ({type(error).__name__})") from None


def send_telegram(message, token, chat_id, session=requests):
    if not token or not chat_id:
        raise ValueError("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID for --telegram")
    try:
        response = session.post(f"https://api.telegram.org/bot{token}/sendMessage",
                                data={"chat_id": chat_id, "text": message[:4096]}, timeout=TIMEOUT)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or payload.get("ok") is not True:
            raise FeedError("Telegram rejected the message")
    except (requests.RequestException, ValueError):
        raise FeedError("Telegram delivery failed") from None


def run(telegram=False, session=requests):
    headlines, failures = [], []
    for url, source in SOURCES:
        try:
            headlines.extend(get_rss(url, source, session=session))
        except FeedError as error:
            failures.append(str(error))
    for title in headlines:
        print(title)
    for error in failures:
        print(error, file=sys.stderr)
    if not headlines:
        print("No headlines retrieved; this is not evidence of no news.", file=sys.stderr)
        return 1
    if telegram:
        message = "Social Scanner\n\n" + "\n".join(headlines)
        if failures:
            message += "\n\nSome sources were unavailable."
        send_telegram(message, os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID"), session)
    return 1 if failures else 0


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--telegram", action="store_true", help="Opt in to message delivery")
    parser.add_argument("--interval", type=int, default=600, help="Seconds between refreshes")
    args = parser.parse_args()
    if args.interval < 1:
        parser.error("--interval must be positive")
    if args.telegram and not (os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID")):
        parser.error("--telegram requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
    try:
        while True:
            try:
                status = run(args.telegram)
            except FeedError as error:
                print(str(error), file=sys.stderr)
                status = 1
            if args.once:
                return status
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
