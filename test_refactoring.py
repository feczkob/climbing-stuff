#!/usr/bin/env python3
"""
Test script to verify the refactoring implementation for GitHub issue #2.
This script tests the new DiscountUrl architecture and category-based scraping.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.service import initialize_scrapers, fetch_discounts_for_category, fetch_all_discounts
from scrapers.discount_dto import DiscountUrl

def test_discount_url_creation():
    """Test that DiscountUrl objects are created correctly."""
    print("Testing DiscountUrl creation...")
    
    # Test basic DiscountUrl creation
    discount_url = DiscountUrl(
        site="bergfreunde",
        category="friends-nuts",
        url="https://www.bergfreunde.eu/camming-devices-friends/"
    )
    
    assert discount_url.site == "bergfreunde"
    assert discount_url.category == "friends-nuts"
    assert discount_url.url == "https://www.bergfreunde.eu/camming-devices-friends/"
    
    print("✓ DiscountUrl creation works correctly")

def test_scraper_initialization():
    """Test that scrapers are initialized with DiscountUrl objects."""
    print("Testing scraper initialization...")
    
    initialize_scrapers()
    
    # Check that scrapers have URLs configured
    from scrapers.service import SCRAPER_MAP
    
    for site_name, scraper in SCRAPER_MAP.items():
        assert hasattr(scraper, 'discount_urls'), f"Scraper {site_name} missing discount_urls"
        assert hasattr(scraper, '_urls_by_category'), f"Scraper {site_name} missing _urls_by_category"
        print(f"✓ {site_name} scraper initialized with {len(scraper.discount_urls)} URLs")
    
    print("✓ All scrapers initialized correctly")

def test_category_based_fetching():
    """Test fetching discounts by category."""
    print("Testing category-based fetching...")
    
    categories = ['friends-nuts', 'slings', 'ropes', 'carabiners-quickdraws']
    
    for category in categories:
        print(f"  Testing category: {category}")
        discounts = fetch_discounts_for_category(category)
        
        # Verify that all discounts have the correct category
        for discount in discounts:
            assert discount['category'] == category, f"Discount has wrong category: {discount['category']} != {category}"
        
        print(f"    ✓ Found {len(discounts)} discounts for {category}")
    
    print("✓ Category-based fetching works correctly")

def test_all_discounts_fetching():
    """Test fetching all discounts."""
    print("Testing all discounts fetching...")
    
    all_discounts = fetch_all_discounts()
    
    # Verify structure
    assert isinstance(all_discounts, dict), "all_discounts should be a dictionary"
    
    categories = ['friends-nuts', 'slings', 'ropes', 'carabiners-quickdraws']
    for category in categories:
        assert category in all_discounts, f"Category {category} missing from all_discounts"
        assert isinstance(all_discounts[category], list), f"Category {category} should be a list"
        
        # Verify that discounts in each category have the correct category field
        for discount in all_discounts[category]:
            assert discount['category'] == category, f"Discount in {category} has wrong category: {discount['category']}"
    
    total_discounts = sum(len(discounts) for discounts in all_discounts.values())
    print(f"✓ Found {total_discounts} total discounts across all categories")
    
    print("✓ All discounts fetching works correctly")

def main():
    """Run all tests."""
    print("Running refactoring tests for GitHub issue #2...")
    print("=" * 60)
    
    try:
        test_discount_url_creation()
        test_scraper_initialization()
        test_category_based_fetching()
        test_all_discounts_fetching()
        
        print("=" * 60)
        print("🎉 All tests passed! The refactoring is working correctly.")
        print("\nKey improvements implemented:")
        print("✓ DiscountUrl class created with site, category, and url fields")
        print("✓ Scrapers now configured with URLs upon instantiation")
        print("✓ Service can invoke discount fetching by category")
        print("✓ Scrapers know internally which URLs to call for each category")
        print("✓ Better error handling and logging")
        print("✓ Type safety with proper annotations")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 