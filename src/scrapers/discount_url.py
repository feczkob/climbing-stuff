"""
DiscountUrl data transfer object.
Represents a URL for a specific category that should be scraped.
"""

from dataclasses import dataclass


@dataclass
class DiscountUrl:
    """Represents a URL for a specific category that should be scraped."""
    category: str
    url: str 