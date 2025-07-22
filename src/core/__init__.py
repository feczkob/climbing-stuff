"""
Core package for the climbing gear discount aggregator.
Contains the main business logic and management classes.
"""

from src.core.manager import ScraperManager
from src.core.content_loader import ContentLoader, HttpContentLoader, MockContentLoader

__all__ = [
    'ScraperManager',
    'ContentLoader',
    'HttpContentLoader',
    'MockContentLoader',
] 