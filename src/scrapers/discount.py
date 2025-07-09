from dataclasses import dataclass
from typing import Optional


@dataclass
class Discount:
    product: str
    url: str
    image_url: Optional[str]
    old_price: Optional[str]
    new_price: Optional[str]
    category: Optional[str] = None
    site: Optional[str] = None
    discount_percent: Optional[str] = None

    def to_dict(self):
        return {
            'product': self.product,
            'url': self.url,
            'image_url': self.image_url,
            'old_price': self.old_price,
            'new_price': self.new_price,
            'category': self.category,
            'site': self.site,
            'discount_percent': self.discount_percent,
        }
