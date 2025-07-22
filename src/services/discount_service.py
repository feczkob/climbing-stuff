import concurrent.futures
from typing import List, Dict, Any

from src.core.config import config
from src.core.logging_config import logger
from src.dto.discount import Discount

# Global instances
ALL_DISCOUNTS = {}
DISCOUNTS_LOADED = False

# Load categories at module level
CATEGORIES = config.get_categories()

# Public API methods
def fetch_discounts_for_category(category: str) -> List[Discount]:
    """Fetch discounts for a specific category from all scrapers."""
    from src.core.manager import ScraperManager
    scraper_manager = ScraperManager()
    scrapers = scraper_manager.get_scrapers()
    
    all_discounts = []
    
    for site_name, scraper in scrapers.items():
        try:
            discounts = scraper.extract_discounts_by_category(category)
            # Add site information to each discount
            for discount in discounts:
                discount.site = site_name.capitalize()
            all_discounts.extend(discounts)
        except Exception as e:
            logger.error(f"Error fetching discounts from {site_name} for category {category}: {e}")
    
    all_discounts.sort(key=lambda d: d.discount_percent, reverse=True)
    return all_discounts

def fetch_all_discounts() -> Dict[str, List[Discount]]:
    """Fetch all discounts using the new category-based architecture."""
    categories = config.get_categories()
    all_discounts = {cat: [] for cat in categories.keys()}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_category = {
            executor.submit(fetch_discounts_for_category, category): category
            for category in categories.keys()
        }

        for future in concurrent.futures.as_completed(future_to_category):
            category = future_to_category[future]
            try:
                discounts = future.result()
                all_discounts[category].extend(discounts)
            except Exception as e:
                logger.error(f"Error processing category {category}: {e}")
    
    return all_discounts

def refresh_discounts_job():
    """Refresh all discounts and update the global cache."""
    global ALL_DISCOUNTS
    discounts = fetch_all_discounts()
    
    # Convert Discount objects to dictionaries for the cache
    discounts_dict = {}
    for category, discount_list in discounts.items():
        discounts_dict[category] = [discount.model_dump() for discount in discount_list]
    
    ALL_DISCOUNTS.clear()
    ALL_DISCOUNTS.update(discounts_dict)
    
    logger.info(f"Discounts refreshed for {len(discounts)} categories.")