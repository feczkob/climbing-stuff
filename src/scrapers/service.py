import concurrent.futures
from typing import List, Dict, Any

from logging_config import logger
from src.core.manager import ScraperManager
from src.scrapers.discount_dto import DiscountUrl

# Global instances
scraper_manager = ScraperManager()
ALL_DISCOUNTS = {}
DISCOUNTS_LOADED = False

# Load categories at module level
CATEGORIES = scraper_manager.load_categories()

# Public API methods
def fetch_discounts_for_category(category: str) -> List[Dict[str, Any]]:
    """Fetch discounts for a specific category from all scrapers."""
    scrapers = scraper_manager.get_scrapers()
    
    all_discounts = []
    
    for site_name, scraper in scrapers.items():
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
    scrapers = scraper_manager.get_scrapers()
    
    categories = scraper_manager.load_categories()
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