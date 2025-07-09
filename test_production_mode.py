#!/usr/bin/env python3
"""
Test script to demonstrate production mode functionality.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import config
from src.services.discount_service import fetch_discounts_for_category

def test_production_mode():
    """Test the production mode functionality."""
    print("🧪 Testing Production Mode Functionality")
    print("=" * 50)
    
    # Test current mode
    mode = "PRODUCTION" if config.is_production() else "DEVELOPMENT"
    print(f"Current mode: {mode}")
    print(f"Mock files directory: {config.get_mock_files_dir()}")
    
    # Test fetching discounts for ropes category
    print(f"\n📊 Fetching discounts for 'ropes' category...")
    try:
        discounts = fetch_discounts_for_category('ropes')
        print(f"✅ Found {len(discounts)} discounts")
        
        # Group by site
        by_site = {}
        for discount in discounts:
            site = discount.site
            if site not in by_site:
                by_site[site] = []
            by_site[site].append(discount)
        
        print(f"\n📋 Discounts by site:")
        for site, site_discounts in by_site.items():
            print(f"  {site}: {len(site_discounts)} discounts")
            if site_discounts:
                # Show first discount as example
                first = site_discounts[0]
                print(f"    Example: {first.product} - {first.discount_percent}% off")
    
    except Exception as e:
        print(f"❌ Error fetching discounts: {e}")
    
    print(f"\n💡 To switch modes:")
    print(f"  Development (mock files): export PRODUCTION_MODE=false")
    print(f"  Production (real scrapers): export PRODUCTION_MODE=true")

if __name__ == "__main__":
    test_production_mode() 