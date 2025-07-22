"""
Scrapers package for the climbing gear discount aggregator.
Contains individual scraper implementations and data models.
"""

from src.scrapers.bergfreunde import BergfreundeScraper
from src.scrapers.mountex import MountexScraper
from src.scrapers.fourcamping import FourCampingScraper
from src.scrapers.maszas import MaszasScraper
from src.scrapers.discount_scraper import DiscountScraper

__all__ = [
    'BergfreundeScraper',
    'MountexScraper',
    'FourCampingScraper',
    'MaszasScraper',
    'DiscountScraper'
] 