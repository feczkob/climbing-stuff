import yaml
import os
import concurrent.futures
from typing import List, Dict, Any

from logging_config import logger
from scrapers.bergfreunde import BergfreundeScraper
from scrapers.fourcamping import FourCampingScraper
from scrapers.mountex import MountexScraper
from scrapers.discount_dto import DiscountUrl

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
CATEGORIES_FILE = os.path.join(CONFIG_DIR, 'categories.yaml')
SITES_FILE = os.path.join(CONFIG_DIR, 'sites.yaml')

# Global scraper instances - will be initialized with DiscountUrl objects
SCRAPER_MAP = {}
ALL_DISCOUNTS = {}
DISCOUNTS_LOADED = False

def load_categories() -> Dict[str, Any]:
    with open(CATEGORIES_FILE, 'r') as f:
        categories_yaml = yaml.safe_load(f)
    return categories_yaml['categories']

CATEGORIES = load_categories()

def load_sites() -> List[Dict[str, Any]]:
    with open(SITES_FILE, 'r') as f:
        sites_yaml = yaml.safe_load(f)
    return [site for site in sites_yaml['sites'] if site.get('enabled', True)]

def create_discount_urls() -> List[DiscountUrl]:
    """Create DiscountUrl objects from the categories configuration."""
    discount_urls = []
    categories = load_categories()
    sites = load_sites()
    
    for category_name, site_urls in categories.items():
        for site in sites:
            site_name = site['name']
            url = site_urls.get(site_name)
            if url and site_name in ['bergfreunde', 'mountex', '4camping']:
                # Handle both single URLs and lists of URLs
                urls = url if isinstance(url, list) else [url]
                for single_url in urls:
                    discount_urls.append(DiscountUrl(
                        site=site_name,
                        category=category_name,
                        url=single_url
                    ))
    
    return discount_urls

def initialize_scrapers():
    """Initialize scrapers with their respective DiscountUrl objects."""
    global SCRAPER_MAP
    
    discount_urls = create_discount_urls()
    
    # Group URLs by site
    urls_by_site = {}
    for discount_url in discount_urls:
        if discount_url.site not in urls_by_site:
            urls_by_site[discount_url.site] = []
        urls_by_site[discount_url.site].append(discount_url)
    
    # Initialize scrapers with their URLs
    scraper_classes = {
        'bergfreunde': BergfreundeScraper,
        'mountex': MountexScraper,
        '4camping': FourCampingScraper,
    }
    
    for site_name, urls in urls_by_site.items():
        if site_name in scraper_classes:
            SCRAPER_MAP[site_name] = scraper_classes[site_name](urls)
            logger.info(f"Initialized {site_name} scraper with {len(urls)} URLs")

def fetch_discounts_for_category(category: str) -> List[Dict[str, Any]]:
    """Fetch discounts for a specific category from all scrapers."""
    if not SCRAPER_MAP:
        initialize_scrapers()
    
    all_discounts = []
    
    for site_name, scraper in SCRAPER_MAP.items():
        try:
            discounts = scraper.extract_discounts_by_category(category)
            # Convert to dictionaries and add site information
            for discount in discounts:
                discount.site = site_name.capitalize()
                all_discounts.append(discount.to_dict())
        except Exception as e:
            logger.error(f"Error fetching discounts from {site_name} for category {category}: {e}")
    
    return all_discounts

def fetch_all_discounts() -> Dict[str, List[Dict[str, Any]]]:
    """Fetch all discounts using the new category-based architecture."""
    if not SCRAPER_MAP:
        initialize_scrapers()
    
    categories = load_categories()
    discounts_by_category = {cat: [] for cat in categories.keys()}
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all category fetching tasks
        future_to_category = {
            executor.submit(fetch_discounts_for_category, category): category 
            for category in categories.keys()
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_category):
            category = future_to_category[future]
            try:
                discounts = future.result()
                discounts_by_category[category].extend(discounts)
            except Exception as e:
                logger.error(f"Error processing category {category}: {e}")
    
    return discounts_by_category

def refresh_discounts_job():
    """Refresh all discounts and update the global cache."""
    global ALL_DISCOUNTS
    discounts = fetch_all_discounts()
    
    ALL_DISCOUNTS.clear()
    ALL_DISCOUNTS.update(discounts)
    
    logger.info(f"Discounts refreshed for {len(discounts)} categories.")