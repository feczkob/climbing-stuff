import yaml
import os
import concurrent.futures

from logging_config import logger
from scrapers.bergfreunde import BergfreundeScraper
from scrapers.fourcamping import FourCampingScraper
from scrapers.mountex import MountexScraper

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
CATEGORIES_FILE = os.path.join(CONFIG_DIR, 'categories.yaml')
SITES_FILE = os.path.join(CONFIG_DIR, 'sites.yaml')

SCRAPER_MAP = {
    'bergfreunde': BergfreundeScraper(),
    'mountex': MountexScraper(),
    '4camping': FourCampingScraper(),
}

ALL_DISCOUNTS = {}
DISCOUNTS_LOADED = False

def load_categories():
    with open(CATEGORIES_FILE, 'r') as f:
        categories_yaml = yaml.safe_load(f)
    return categories_yaml['categories']
CATEGORIES = load_categories()

def load_sites():
    with open(SITES_FILE, 'r') as f:
        sites_yaml = yaml.safe_load(f)
    return [site for site in sites_yaml['sites'] if site.get('enabled', True)]

def fetch_discounts_for_site_category(site_name, cat_name, url):
    discounts = []
    urls = url if isinstance(url, list) else [url]
    for single_url in urls:
        try:
            site_discounts = SCRAPER_MAP[site_name].extract_discounts_from_category(single_url)
        except Exception:
            site_discounts = []
        for d in site_discounts:
            d.site = site_name.capitalize()
            d.category = cat_name
        discounts.extend(site_discounts)
    return cat_name, discounts

def fetch_all_discounts():
    with open(CATEGORIES_FILE, 'r') as f:
        categories = yaml.safe_load(f)['categories']
    category_list = list(categories.keys())
    sites = load_sites()
    discounts_by_category = {cat: [] for cat in category_list}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for cat_name, site_urls in categories.items():
            for site in sites:
                site_name = site['name']
                url = site_urls.get(site_name)
                if url and site_name in SCRAPER_MAP:
                    futures.append(executor.submit(fetch_discounts_for_site_category, site_name, cat_name, url))
        for future in concurrent.futures.as_completed(futures):
            cat_name, discounts = future.result()
            # Convert Discount objects to dictionaries
            discount_dicts = [d.to_dict() for d in discounts]
            discounts_by_category[cat_name].extend(discount_dicts)
    return discounts_by_category

def refresh_discounts_job():
    global ALL_DISCOUNTS
    discounts = fetch_all_discounts()

    # Convert all Discount objects to dictionaries
    converted_discounts = {}
    for category, category_discounts in discounts.items():
        converted_discounts[category] = []
        for discount in category_discounts:
            if hasattr(discount, 'to_dict'):
                converted_discounts[category].append(discount.to_dict())
            else:
                converted_discounts[category].append(discount)

    ALL_DISCOUNTS.clear()
    ALL_DISCOUNTS.update(converted_discounts)

    logger.info(f"Discounts refreshed.")