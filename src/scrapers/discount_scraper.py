from abc import ABC, abstractmethod
from typing import List, Dict
from src.scrapers.discount_url import DiscountUrl


class DiscountScraper(ABC):
    def __init__(self, discount_urls: List[DiscountUrl] = None):
        """
        Initialize scraper with category-specific URLs.
        
        Args:
            discount_urls: List of DiscountUrl objects containing URLs for each category
        """
        self.discount_urls = discount_urls or []
        self._urls_by_category = self._group_urls_by_category()

    def _group_urls_by_category(self):
        urls_by_category = {}
        for discount_url in self.discount_urls:
            urls_by_category.setdefault(discount_url.category, []).append(discount_url.url)
        return urls_by_category

    def get_urls_for_category(self, category: str) -> List[str]:
        """Get all URLs configured for a specific category."""
        return self._urls_by_category.get(category, [])

    @abstractmethod
    def extract_discounts_from_category(self, url):
        """Extract discounts from a given category URL."""
        pass

    def extract_discounts_by_category(self, category: str) -> List:
        """
        Extract discounts for a specific category using configured URLs.
        
        Args:
            category: The category name to fetch discounts for
            
        Returns:
            List of Discount objects
        """
        urls = self.get_urls_for_category(category)
        all_discounts = []
        
        for url in urls:
            try:
                discounts = self.extract_discounts_from_category(url)
                # Add category information to each discount
                for discount in discounts:
                    discount.category = category
                all_discounts.extend(discounts)
            except Exception as e:
                # Log error but continue with other URLs
                from src.core.logging_config import logger
                logger.error(f"Error extracting discounts from {url} for category {category}: {e}")
                
        return all_discounts