"""
Core package for the climbing gear discount aggregator.
Contains the main business logic and management classes.
"""

from src.core.config import config
from src.core.logging_config import logger
from src.core.manager import ScraperManager
from src.core.content_loader import ContentLoader, HttpContentLoader, MockContentLoader, SeleniumContentLoader

__all__ = [
    'config',
    'logger',
    'ScraperManager',
    'ContentLoader',
    'HttpContentLoader',
    'MockContentLoader',
    'SeleniumContentLoader'
] 