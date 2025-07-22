"""
DiscountUrl data transfer object.
Represents a URL for a specific category that should be scraped.
"""

from pydantic import BaseModel


class DiscountUrl(BaseModel):
    """Represents a URL for a specific category that should be scraped."""
    category: str
    url: str 