#!/usr/bin/env python3
"""
Test suite for the scraper functionality.
Tests the DiscountUrl architecture and category-based scraping.
"""

import sys
import os
import unittest
from unittest.mock import patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.discount_service import fetch_discounts_for_category, fetch_all_discounts
from src.scrapers.discount_url import DiscountUrl
from src.core.manager import ScraperManager
from src.scrapers.content_loader import HttpContentLoader, MockContentLoader, SeleniumContentLoader


class TestDiscountUrl(unittest.TestCase):
    """Test cases for DiscountUrl class."""
    
    def test_discount_url_creation(self):
        """Test that DiscountUrl objects are created correctly."""
        discount_url = DiscountUrl(
            category="friends-nuts",
            url="https://www.bergfreunde.eu/camming-devices-friends/"
        )
        
        self.assertEqual(discount_url.category, "friends-nuts")
        self.assertEqual(discount_url.url, "https://www.bergfreunde.eu/camming-devices-friends/")


class TestScraperManager(unittest.TestCase):
    """Test cases for ScraperManager class."""

    @patch('src.core.config.config.is_production', return_value=True)
    def test_scraper_initialization_production(self, mock_is_production):
        """Test that scrapers are initialized with correct content loaders in production."""
        scraper_manager = ScraperManager()
        scrapers = scraper_manager.get_scrapers()

        for site_name, scraper in scrapers.items():
            self.assertIsInstance(scraper.content_loader, (HttpContentLoader, SeleniumContentLoader),
                                  f"Scraper {site_name} has wrong content loader in production")

    @patch('src.core.config.config.is_production', return_value=False)
    def test_scraper_initialization_development(self, mock_is_production):
        """Test that scrapers are initialized with correct content loaders in development."""
        scraper_manager = ScraperManager()
        scrapers = scraper_manager.get_scrapers()

        for site_name, scraper in scrapers.items():
            self.assertIsInstance(scraper.content_loader, MockContentLoader,
                                  f"Scraper {site_name} has wrong content loader in development")

    def test_load_categories(self):
        """Test that categories are loaded correctly."""
        scraper_manager = ScraperManager()
        categories = scraper_manager.load_categories()
        
        self.assertIsInstance(categories, dict)
        self.assertIn('friends-nuts', categories)
        self.assertIn('slings', categories)
        self.assertIn('ropes', categories)
        self.assertIn('carabiners-quickdraws', categories)


class TestServiceLayer(unittest.TestCase):
    """Test cases for the service layer functionality."""
    
    def test_category_based_fetching(self):
        """Test fetching discounts by category."""
        categories = ['friends-nuts', 'slings', 'ropes', 'carabiners-quickdraws']
        
        for category in categories:
            with self.subTest(category=category):
                discounts = fetch_discounts_for_category(category)
                
                # Verify that all discounts have the correct category
                for discount in discounts:
                    self.assertEqual(discount.category, category, 
                                   f"Discount has wrong category: {discount.category} != {category}")
                
                # Verify that discounts have required fields
                for discount in discounts:
                    self.assertTrue(hasattr(discount, 'product'))
                    self.assertTrue(hasattr(discount, 'url'))
                    self.assertTrue(hasattr(discount, 'site'))
                    self.assertTrue(hasattr(discount, 'category'))
    
    def test_all_discounts_fetching(self):
        """Test fetching all discounts."""
        all_discounts = fetch_all_discounts()
        
        # Verify structure
        self.assertIsInstance(all_discounts, dict)
        
        categories = ['friends-nuts', 'slings', 'ropes', 'carabiners-quickdraws']
        for category in categories:
            self.assertIn(category, all_discounts, 
                         f"Category {category} missing from all_discounts")
            self.assertIsInstance(all_discounts[category], list, 
                                f"Category {category} should be a list")
            
            # Verify that discounts in each category have the correct category field
            for discount in all_discounts[category]:
                self.assertEqual(discount.category, category, 
                               f"Discount in {category} has wrong category: {discount.category}")


if __name__ == "__main__":
    unittest.main(verbosity=2) 