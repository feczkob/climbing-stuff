from dataclasses import dataclass
from typing import Optional, List


@dataclass
class DiscountUrl:
    """Represents a URL for scraping discounts from a specific site and category."""
    site: str
    category: str
    url: str
    
    def __post_init__(self):
        # Ensure site name is properly formatted
        self.site = self.site.lower()


class Discount:
    def __init__(self, product, url, image_url, original_price, discounted_price, site, discount_percent=None, category=None):
        self.product = product
        self.url = url
        self.image_url = image_url
        self.original_price = original_price
        self.discounted_price = discounted_price
        self.site = site
        self.discount_percent = discount_percent
        self.category = category

    def to_dict(self):
        return {
            "product": self.product,
            "url": self.url,
            "image_url": self.image_url,
            "original_price": self.original_price,
            "discounted_price": self.discounted_price,
            "site": self.site,
            "discount_percent": self.discount_percent,
            "category": self.category
        }
