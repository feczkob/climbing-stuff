#!/usr/bin/env python3
"""
CLI tool for the climbing gear discount aggregator.
Provides command-line access to fetch and display discounts.
"""

import sys
import os
import argparse
from typing import List, Dict, Any

# Add the project root to the path (simplified)
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.services.discount_service import fetch_discounts_for_category, fetch_all_discounts
from src.core.manager import ScraperManager


def print_discounts_category(category: str, discounts: List[Any], show_images: bool = True):
    """Print discounts for a specific category with improved formatting."""
    if not discounts:
        print(f"\n[{category}] No discounts found.")
        return
    
    print(f"\n[{category.upper()}] {len(discounts)} discounts found:")
    print("=" * 60)
    
    for i, discount in enumerate(discounts, 1):
        # Handle both Discount objects and dictionaries
        if hasattr(discount, 'product'):
            # Discount object
            product = discount.product
            site = discount.site
            url = discount.url
            image_url = discount.image_url
            old_price = discount.old_price
            new_price = discount.new_price
        else:
            # Dictionary (fallback)
            product = discount['product']
            site = discount['site']
            url = discount['url']
            image_url = discount.get('image_url')
            old_price = discount.get('old_price')
            new_price = discount.get('new_price')
        
        print(f"{i:2d}. {product}")
        print(f"    Site: {site}")
        print(f"    URL: {url}")
        if show_images and image_url:
            print(f"    Image: {image_url}")
        if old_price and new_price:
            print(f"    Price: {old_price} → {new_price}")
        print()


def print_summary(all_discounts: Dict[str, List[Any]]):
    """Print a summary of all discounts."""
    total_discounts = sum(len(discounts) for discounts in all_discounts.values())
    print(f"\n📊 SUMMARY: {total_discounts} total discounts across {len(all_discounts)} categories")
    
    for category, discounts in all_discounts.items():
        if discounts:
            # Extract site names from Discount objects or dictionaries
            sites = set()
            for discount in discounts:
                if hasattr(discount, 'site'):
                    sites.add(discount.site)
                else:
                    sites.add(discount['site'])
            print(f"   {category}: {len(discounts)} discounts from {', '.join(sites)}")


def fetch_by_category(category: str, show_images: bool = True):
    """Fetch and display discounts for a specific category."""
    try:
        print(f"Fetching discounts for category: {category}")
        discounts = fetch_discounts_for_category(category)
        print_discounts_category(category, discounts, show_images)
        return discounts
    except Exception as e:
        print(f"❌ Error fetching discounts for {category}: {e}")
        return []


def fetch_all(show_images: bool = True, show_summary: bool = True):
    """Fetch and display all discounts."""
    try:
        print("🔄 Fetching all discounts...")
        all_discounts = fetch_all_discounts()
        
        for category, discounts in all_discounts.items():
            print_discounts_category(category, discounts, show_images)
        
        if show_summary:
            print_summary(all_discounts)
        
        return all_discounts
    except Exception as e:
        print(f"❌ Error fetching all discounts: {e}")
        return {}


def list_categories():
    """List all available categories."""
    try:
        scraper_manager = ScraperManager()
        categories = scraper_manager.load_categories()
        print("📋 Available categories:")
        for category in categories.keys():
            print(f"   - {category}")
    except Exception as e:
        print(f"❌ Error listing categories: {e}")


def main():
    """Main CLI function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="CLI tool for the climbing gear discount aggregator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                    # Fetch all discounts
  python cli.py --category friends-nuts  # Fetch specific category
  python cli.py --list-categories  # List available categories
  python cli.py --no-images        # Hide image URLs
  python cli.py --no-summary       # Hide summary
        """
    )
    
    parser.add_argument(
        '--category', '-c',
        help='Fetch discounts for a specific category'
    )
    
    parser.add_argument(
        '--list-categories', '-l',
        action='store_true',
        help='List all available categories'
    )
    
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Hide image URLs in output'
    )
    
    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Hide summary statistics'
    )
    
    args = parser.parse_args()
    
    # Handle different commands
    if args.list_categories:
        list_categories()
    elif args.category:
        fetch_by_category(args.category, not args.no_images)
    else:
        fetch_all(not args.no_images, not args.no_summary)


if __name__ == "__main__":
    main()