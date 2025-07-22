#!/usr/bin/env python3
"""
Script to fetch HTML responses for all categories from all sites
and save them as mock files for development/testing.
"""

import os
import time
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import httpx

from src.core.config import config


MOCKS_DIR = "tests/mocks"


def fetch_content(url, use_playwright=False):
    """Fetch URL content and return it."""
    try:
        if use_playwright:
            print(f"  Fetching {url} using Playwright...")
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url)
                content = page.content()
                browser.close()
                return content
        else:
            print(f"  Fetching {url} using httpx...")
            response = httpx.get(url, follow_redirects=True, timeout=30)
            response.raise_for_status()
            return response.text
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        if not use_playwright:
            print(f"  Retrying with Playwright...")
            return fetch_content(url, use_playwright=True)
    return ""


def main():
    if not os.path.exists(MOCKS_DIR):
        os.makedirs(MOCKS_DIR)

    categories_data = config.get_categories()

    for category_name, sites in categories_data.items():
        print(f"Processing category: {category_name}")
        for site_name, urls in sites.items():
            url_list = urls if isinstance(urls, list) else [urls]
            url_to_fetch = url_list[0]  # Fetch only the first URL

            file_name = f"{site_name.lower()}_{category_name}.html"
            file_path = os.path.join(MOCKS_DIR, file_name)
            
            print(f"  Site: {site_name}, URL: {url_to_fetch}")
            content = fetch_content(url_to_fetch, use_playwright=(site_name == "mountex"))

            if content:
                soup = BeautifulSoup(content, "html.parser")
                with open(file_path, "w") as f:
                    f.write(str(soup.prettify()))
    print("Done.")


if __name__ == "__main__":
    main() 