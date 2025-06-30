from abc import ABC, abstractmethod

class DiscountScraper(ABC):
    @abstractmethod
    def check_discounts(self):
        """Check all discounts on the main page or default category."""
        pass

    @abstractmethod
    def extract_discounts_from_category(self, url):
        """Extract discounts from a given category URL."""
        pass