#!/usr/bin/env python3
"""
Test suite for the scraper functionality.
Tests the DiscountUrl architecture and category-based scraping.
"""

import sys
import os
import unittest

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.service import fetch_discounts_for_category, fetch_all_discounts
from scrapers.discount_dto import DiscountUrl
from core.manager import ScraperManager


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
    
    def test_scraper_initialization(self):
        """Test that scrapers are initialized with DiscountUrl objects."""
        scraper_manager = ScraperManager()
        scrapers = scraper_manager.get_scrapers()
        
        for site_name, scraper in scrapers.items():
            self.assertTrue(hasattr(scraper, 'discount_urls'), 
                          f"Scraper {site_name} missing discount_urls")
            self.assertTrue(hasattr(scraper, '_urls_by_category'), 
                          f"Scraper {site_name} missing _urls_by_category")
    
    def test_load_categories(self):
        """Test that categories are loaded correctly."""
        scraper_manager = ScraperManager()
        categories = scraper_manager.load_categories()
        
        self.assertIsInstance(categories, dict)
        self.assertIn('friends-nuts', categories)
        self.assertIn('slings', categories)
        self.assertIn('ropes', categories)
        self.assertIn('carabiners-quickdraws', categories)
    
    def test_load_sites(self):
        """Test that sites are loaded correctly."""
        scraper_manager = ScraperManager()
        sites = scraper_manager.load_sites()
        
        self.assertIsInstance(sites, list)
        self.assertTrue(len(sites) > 0)
        
        for site in sites:
            self.assertIn('name', site)
            self.assertIn('enabled', site)


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
                    self.assertEqual(discount['category'], category, 
                                   f"Discount has wrong category: {discount['category']} != {category}")
                
                # Verify that discounts have required fields
                for discount in discounts:
                    self.assertIn('product', discount)
                    self.assertIn('url', discount)
                    self.assertIn('site', discount)
                    self.assertIn('category', discount)
    
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
                self.assertEqual(discount['category'], category, 
                               f"Discount in {category} has wrong category: {discount['category']}")


def run_integration_tests():
    """Run integration tests that actually fetch data from websites."""
    print("Running integration tests for scraper functionality...")
    print("=" * 60)
    
    try:
        # Test DiscountUrl creation
        print("Testing DiscountUrl creation...")
        discount_url = DiscountUrl(
            category="friends-nuts",
            url="https://www.bergfreunde.eu/camming-devices-friends/"
        )
        assert discount_url.category == "friends-nuts"
        assert discount_url.url == "https://www.bergfreunde.eu/camming-devices-friends/"
        print("✓ DiscountUrl creation works correctly")
        
        # Test scraper initialization
        print("Testing scraper initialization...")
        scraper_manager = ScraperManager()
        scrapers = scraper_manager.get_scrapers()
        
        for site_name, scraper in scrapers.items():
            assert hasattr(scraper, 'discount_urls')
            assert hasattr(scraper, '_urls_by_category')
            print(f"✓ {site_name} scraper initialized with {len(scraper.discount_urls)} URLs")
        
        print("✓ All scrapers initialized correctly")
        
        # Test category-based fetching
        print("Testing category-based fetching...")
        categories = ['friends-nuts', 'slings', 'ropes', 'carabiners-quickdraws']
        
        for category in categories:
            print(f"  Testing category: {category}")
            discounts = fetch_discounts_for_category(category)
            
            # Verify that all discounts have the correct category
            for discount in discounts:
                assert discount['category'] == category
            
            print(f"    ✓ Found {len(discounts)} discounts for {category}")
        
        print("✓ Category-based fetching works correctly")
        
        # Test all discounts fetching
        print("Testing all discounts fetching...")
        all_discounts = fetch_all_discounts()
        
        total_discounts = sum(len(discounts) for discounts in all_discounts.values())
        print(f"✓ Found {total_discounts} total discounts across all categories")
        
        print("✓ All discounts fetching works correctly")
        
        print("=" * 60)
        print("🎉 All integration tests passed!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    # Run integration tests
    print("\n" + "="*60)
    run_integration_tests() 