#!/usr/bin/env python3
"""
Script to fetch HTML responses for all categories from all sites
and save them as mock files for development/testing.
"""

import os
import sys
import time
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import httpx

from src.core.config import config

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

MOCKS_DIR = "tests/mocks"

# Define your URLs here
URLS = config.get_all_urls()


def fetch_and_save(url, file_path, use_playwright=False):
    """Fetch URL content and save to a file."""
    try:
        if use_playwright:
            print(f"  Fetching {url} using Playwright...")
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url)
                content = page.content()
                browser.close()
        else:
            print(f"  Fetching {url} using httpx...")
            response = httpx.get(url, follow_redirects=True, timeout=30)
            response.raise_for_status()
            content = response.text

        soup = BeautifulSoup(content, "html.parser")
        with open(file_path, "w") as f:
            f.write(str(soup.prettify()))
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        if not use_playwright:
            fetch_and_save(url, file_path, use_playwright=True)


def main():
    if not os.path.exists(MOCKS_DIR):
        os.makedirs(MOCKS_DIR)

    for site, urls in URLS.items():
        print(f"Processing site: {site}")
        for category, url_list in urls.items():
            for i, url in enumerate(url_list):
                # Create a filename based on the site and category
                file_name = f"{site.lower()}_{category}.html"
                file_path = os.path.join(MOCKS_DIR, file_name)
                # For mountex, use playwright
                fetch_and_save(url, file_path, use_playwright=(site == "mountex"))
    print("Done.")


if __name__ == "__main__":
    main() 