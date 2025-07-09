"""
Scrapers package for the climbing gear discount aggregator.
Contains individual scraper implementations and the service layer.
"""

from .discount_dto import DiscountUrl, Discount

__all__ = [
    'DiscountUrl',
    'Discount'
] 