# Social Scanner

A small command-line RSS/Atom headline reader for CoinTelegraph and Decrypt. It prints public feed titles and optionally sends a summary to Telegram. It does not verify article accuracy, assess token safety, or establish airdrop eligibility.

## Setup

Python 3.10+:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python social_scanner.py --once
python -m unittest discover -s tests -v
```

By default, repeated runs refresh every 600 seconds; use `--interval 900` to change that. Stop with Ctrl+C. A one-shot run exits with code 1 when any source fails or no headlines are available. Errors remain visible; an unavailable feed is not treated as an empty successful result.

## Optional Telegram

Copy `.env.example` to `.env` and configure a bot token and chat ID locally. Delivery requires `python social_scanner.py --once --telegram`. Keep the token private. Messages are limited to 4096 characters. No delivery happens by default.

## Limits

Feeds can change format or become unavailable. The unverified CoinGecko news endpoint has been removed. This tool supports standard RSS 2.0 and Atom feeds, rejects XML entity declarations, and limits feed downloads to 2 MB. It displays up to three nonempty titles per source; repeated runs may repeat headlines. Regression tests use mocked HTTP responses and do not certify live source availability.
