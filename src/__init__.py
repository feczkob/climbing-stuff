"""
Main package for the climbing gear discount aggregator.
Contains all application code organized in sub-packages.
"""

from . import app
from . import core
from . import scrapers
from . import services

__all__ = ['app', 'core', 'scrapers', 'services']
