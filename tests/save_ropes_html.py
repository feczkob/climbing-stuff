#!/usr/bin/env python3
"""
Script to fetch and save HTML responses from all sites for the 'ropes' category.
Useful for testing and debugging scrapers.
"""

import sys
import os
import time
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import yaml

# Load categories from YAML file
def load_categories():
    categories_file = os.path.join(project_root, 'config', 'categories.yaml')
    with open(categories_file, 'r') as f:
        categories_yaml = yaml.safe_load(f)
    return categories_yaml['categories']

def save_html_file(url: str, html_content: str, site_name: str):
    """Save HTML content to a file in the mocks directory."""
    # Create a safe filename from the URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('.', '_').replace('www_', '')
    path = parsed_url.path.replace('/', '_').replace('-', '_')
    if path.startswith('_'):
        path = path[1:]
    if path.endswith('_'):
        path = path[:-1]
    
    filename = f"{site_name}_{domain}_{path}.html"
    filepath = os.path.join(project_root, 'tests', 'mocks', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Saved: {filename}")
    return filepath

def fetch_with_requests(url: str, site_name: str):
    """Fetch HTML using requests library."""
    try:
        print(f"🌐 Fetching {site_name} with requests: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        save_html_file(url, response.text, site_name)
        return True
    except Exception as e:
        print(f"❌ Error fetching {site_name} with requests: {e}")
        return False

def fetch_with_selenium(url: str, site_name: str):
    """Fetch HTML using Selenium (for JavaScript-heavy sites)."""
    try:
        print(f"🌐 Fetching {site_name} with Selenium: {url}")
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript to load
        
        html_content = driver.page_source
        driver.quit()
        
        save_html_file(url, html_content, site_name)
        return True
    except Exception as e:
        print(f"❌ Error fetching {site_name} with Selenium: {e}")
        return False

def main():
    """Main function to fetch HTML from all sites for the ropes category."""
    print("🚀 Starting HTML fetch for 'ropes' category...")
    
    # Load categories and get the ropes category URLs
    categories = load_categories()
    ropes_urls = categories.get('ropes', {})
    
    if not ropes_urls:
        print("❌ No URLs found for 'ropes' category")
        return
    
    print(f"📋 Found {len(ropes_urls)} sites for ropes category:")
    for site, url in ropes_urls.items():
        print(f"  - {site}: {url}")
    
    print("\n" + "="*60)
    
    # Fetch HTML from each site
    for site_name, url in ropes_urls.items():
        print(f"\n🎯 Processing {site_name.upper()}...")
        
        # Use Selenium for Mountex (JavaScript-heavy), requests for others
        if site_name == 'mountex':
            success = fetch_with_selenium(url, site_name)
        else:
            success = fetch_with_requests(url, site_name)
        
        if success:
            print(f"✅ Successfully saved {site_name} HTML")
        else:
            print(f"❌ Failed to save {site_name} HTML")
        
        # Small delay between requests
        time.sleep(2)
    
    print(f"\n🎉 Finished! HTML files saved to: {os.path.join(project_root, 'tests', 'mocks')}")
    
    # List saved files
    mocks_dir = os.path.join(project_root, 'tests', 'mocks')
    saved_files = [f for f in os.listdir(mocks_dir) if f.endswith('.html')]
    if saved_files:
        print(f"\n📁 Saved files:")
        for file in saved_files:
            print(f"  - {file}")

if __name__ == "__main__":
    main() 