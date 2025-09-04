#!/usr/bin/env python3
"""
Monitor new products added to the Dead.net store.

This script checks the Dead.net store's "all products" collection and sends a notification via ntfy if any new products are detected.

Configuration via environment variables:
 - NTFY_STORE_TOPIC: ntfy topic to which notifications should be sent.
   If not set, the script will attempt to use NTFY_TOPIC.
"""

import os
import sys
import json
import requests
from bs4 import BeautifulSoup

def get_env(name, default=None):
    value = os.getenv(name)
    return value if value is not None else default

def fetch_product_titles():
    """
    Fetch a list of product titles from the Dead.net store.
    Returns a list of strings. If an error occurs, returns an empty list.
    """
    url = "https://store.dead.net/collections/all?sort_by=created-descending"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception as exc:
        print(f"Error fetching store page: {exc}", file=sys.stderr)
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    titles = []
    # product titles may be within h2 or h3 tags with class containing product name
    for heading in soup.find_all(["h2", "h3"]):
        text = heading.get_text(strip=True)
        if text:
            titles.append(text)
    return titles

def send_notification(topic: str, message: str):
    """
    Send a notification via ntfy. Returns True on success, False otherwise.
    """
    if not topic:
        print("NTFY_STORE_TOPIC is not set. Skipping notification.", file=sys.stderr)
        return False
    url = f"https://ntfy.sh/{topic}"
    try:
        r = requests.post(url, data=message.encode("utf-8"), timeout=30)
        r.raise_for_status()
    except Exception as exc:
        print(f"Error sending notification: {exc}", file=sys.stderr)
        return False
    return True

def main():
    topic = get_env("NTFY_STORE_TOPIC") or get_env("NTFY_TOPIC")
    product_titles = fetch_product_titles()
    if not product_titles:
        return
    cache_file = ".store_monitor_cache.json"
    last_seen = []
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                last_seen = json.load(f)
        except Exception:
            last_seen = []
    # Determine new product titles not seen in previous run
    new_titles = [t for t in product_titles if t not in last_seen]
    if new_titles:
        for title in new_titles:
            send_notification(topic, f"New product added: {title}")
        # update cache with current titles (limit to first 50 to keep file small)
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(product_titles[:50], f)
        except Exception as exc:
            print(f"Error writing cache file: {exc}", file=sys.stderr)

if __name__ == "__main__":
    main()
