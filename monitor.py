"""
Monitor script for the United States of Dead collection.

This script periodically checks the Dead.net "United States of Dead" collection for a specific state and size.  If the product
page is found and the desired size is available, it sends a notification via ntfy.  If the page exists but the size is
sold out, it also notifies accordingly.  When the page does not yet exist, it notifies that the page is still missing.

Configuration is driven by environment variables:
    STATE_KEYWORD:  The state to monitor (e.g. "indiana").  Default: "indiana".
    SIZE_KEYWORD:   The size to monitor (e.g. "large").  Default: "large".
    NTFY_TOPIC:     The ntfy topic to which notifications should be sent.  If unset, no notifications are sent.

Usage:
    python monitor.py

Dependencies:
    - requests
    - beautifulsoup4

Note: This script uses the public product JSON endpoint provided by Shopify (appended with `.json` to the product URL) to
determine availability.  It is not affiliated with Dead.net and may break if their site structure changes.
"""

import os
import sys
import json
import requests
from bs4 import BeautifulSoup

def get_env(name: str, default: str | None = None) -> str | None:
    """Return the value of an environment variable or a default if not set."""
    value = os.getenv(name)
    return value if value is not None else default


def find_product_page(state_keyword: str) -> str | None:
    """Search the United States of Dead collection for a product matching the given state keyword.

    Args:
        state_keyword: The state name to search for (case-insensitive).

    Returns:
        The full URL of the product page if found, or None otherwise.
    """
    collection_url = "https://store.dead.net/collections/united-states-of-dead"
    try:
        response = requests.get(collection_url, timeout=30)
        response.raise_for_status()
    except Exception as exc:
        print(f"Error fetching collection page: {exc}", file=sys.stderr)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    for link in links:
        text = link.get_text(strip=True).lower()
        if state_keyword.lower() in text:
            href = link["href"]
            # Build full URL if necessary
            if href.startswith("/"):
                return f"https://store.dead.net{href}"
            return href
    return None


def check_variant_available(product_url: str, size_keyword: str) -> bool | None:
    """Check if the product variant with the given size keyword is available.

    Args:
        product_url: The URL of the product page.
        size_keyword: The size to search for (case-insensitive).

    Returns:
        True if available, False if sold out, or None if the variant is not found.
    """
    json_url = product_url.rstrip("/") + ".json"
    try:
        resp = requests.get(json_url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"Error fetching product JSON: {exc}", file=sys.stderr)
        return None
    product = data.get("product")
    if not product:
        return None
    variants = product.get("variants", [])
    for variant in variants:
        title = variant.get("title", "").lower()
        if size_keyword.lower() in title:
            return variant.get("available", False)
    return None


def send_notification(topic: str | None, message: str) -> None:
    """Send a notification to the given ntfy topic if one is provided."""
    if not topic:
        # If no topic is configured, print to stdout for debugging
        print(message)
        return
    try:
        requests.post(f"https://ntfy.sh/{topic}", data=message.encode("utf-8"), timeout=10)
    except Exception as exc:
        print(f"Error sending notification: {exc}", file=sys.stderr)


def main() -> None:
    state_keyword = get_env("STATE_KEYWORD", "indiana")
    size_keyword = get_env("SIZE_KEYWORD", "large")
    ntfy_topic = get_env("NTFY_TOPIC")

    product_url = find_product_page(state_keyword)
    if not product_url:
        send_notification(ntfy_topic, f"{state_keyword.title()} shirt page is not yet available.")
        return

    available = check_variant_available(product_url, size_keyword)
    if available is None:
        send_notification(ntfy_topic, f"{state_keyword.title()} product found, but the {size_keyword.title()} variant is missing.")
    elif available:
        send_notification(ntfy_topic, f"{state_keyword.title()} {size_keyword.title()} is available! {product_url}")
    else:
        send_notification(ntfy_topic, f"{state_keyword.title()} {size_keyword.title()} is currently sold out. {product_url}")


if __name__ == "__main__":
    main()