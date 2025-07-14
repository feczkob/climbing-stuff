from abc import ABC, abstractmethod
from typing import List, Optional

from src.core.logging_config import logger
from src.scrapers.discount import Discount
from src.scrapers.discount_url import DiscountUrl


class DiscountScraper(ABC):
    """Abstract base class for discount scrapers."""

    def __init__(self, discount_urls: Optional[List[DiscountUrl]] = None):
        """
        Initialize a new DiscountScraper.

        :param discount_urls: A list of DiscountUrl objects.
        """
        self.discount_urls = discount_urls if discount_urls is not None else []

    def get_urls_by_category(self, category: str) -> List[str]:
        """Get all URLs for a specific category."""
        return [du.url for du in self.discount_urls if du.category == category]

    @abstractmethod
    def extract_discounts_from_category(self, url: str, category: str, site: str) -> List[Discount]:
        """
        Abstract method to extract discounts from a category page.

        :param url: The URL of the category page.
        :param category: The category being scraped.
        :param site: The site being scraped.
        :return: A list of Discount objects.
        """
        pass

    def extract_discounts_by_category(self, category: str, site: str) -> List[Discount]:
        """
        Extract all discounts for a given category.

        This method iterates over all URLs registered for a category,
        calls the scraper for each URL, and aggregates the results.

        :param category: The category to scrape.
        :param site: The site being scraped.
        :return: A list of Discount objects.
        """
        logger.info(f"[{self.__class__.__name__}] Starting extraction for category '{category}'...")

        urls_for_category = self.get_urls_by_category(category)
        all_discounts: List[Discount] = []

        for url in urls_for_category:
            try:
                logger.info(f"[{self.__class__.__name__}] Scraping URL: {url}")
                discounts = self.extract_discounts_from_category(url, category, site)
                all_discounts.extend(discounts)
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Error scraping {url}: {e}")

        logger.info(f"[{self.__class__.__name__}] Found {len(all_discounts)} discounts for category '{category}'.")
        return all_discounts