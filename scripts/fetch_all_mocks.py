#!/usr/bin/env python3
"""
Script to fetch HTML responses for all categories from all sites
and save them as mock files for development/testing.
"""

import os
import sys
import yaml
import requests
from pathlib import Path
from urllib.parse import urlparse
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import not needed for this script
# from src.core.config import Config

def fetch_html(url, headers=None, site_name=None):
    """Fetch HTML content from URL with retry logic."""
    if site_name == "mountex":
        try:
            print(f"  Fetching {url} using Selenium...")
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(5)  # Wait for dynamic content
            html = driver.page_source
            driver.quit()
            return html
        except Exception as e:
            print(f"  Error fetching {url} with Selenium: {e}")
            return None

    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"  Fetching {url} (attempt {attempt + 1})")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print(f"  Failed to fetch {url} after {max_retries} attempts")
                return None

def generate_mock_filename(site_name, url, category):
    """Generate mock filename based on site, URL, and category."""
    return f"{site_name}_{category}.html"

def main():
    """Main function to fetch all mock files."""
    # Load categories configuration
    config_path = Path(__file__).parent.parent / 'config' / 'categories.yaml'
    with open(config_path, 'r') as f:
        categories_config = yaml.safe_load(f)
    
    # Create mocks directory
    mocks_dir = Path(__file__).parent.parent / 'tests' / 'mocks'
    mocks_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Starting to fetch HTML responses for all categories...")
    print(f"📁 Mock files will be saved to: {mocks_dir}")
    
    total_files = 0
    successful_files = 0
    
    for category_name, sites in categories_config['categories'].items():
        print(f"\n📂 Processing category: {category_name}")
        
        for site_name, urls in sites.items():
            if isinstance(urls, str):
                urls = [urls]
            
            for url in urls:
                total_files += 1
                filename = generate_mock_filename(site_name, url, category_name)
                filepath = mocks_dir / filename
                
                print(f"  📄 {filename}")
                
                # Skip if file already exists
                if filepath.exists():
                    print(f"    ⏭️  File already exists, skipping...")
                    successful_files += 1
                    continue
                
                # Fetch HTML content
                html_content = fetch_html(url, site_name=site_name)
                
                if html_content:
                    # Save to file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f"    ✅ Saved {len(html_content)} characters")
                    successful_files += 1
                else:
                    print(f"    ❌ Failed to fetch content")
                
                # Small delay between requests
                time.sleep(1)
    
    print(f"\n🎉 Fetching complete!")
    print(f"📊 Summary: {successful_files}/{total_files} files successfully created")
    
    if successful_files < total_files:
        print(f"⚠️  {total_files - successful_files} files failed to fetch")
        print("   You may need to check the URLs or network connection")

if __name__ == "__main__":
    main() 