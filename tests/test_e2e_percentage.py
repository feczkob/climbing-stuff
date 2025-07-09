#!/usr/bin/env python3
"""
E2E test suite for discount percentage format.
Tests that percentage values are correctly formatted as numeric strings without % symbol.
"""

import sys
import os
import unittest
import json
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.discount_service import fetch_discounts_for_category, fetch_all_discounts
from src.scrapers.bergfreunde import BergfreundeScraper
from src.scrapers.mountex import MountexScraper
from src.scrapers.fourcamping import FourCampingScraper
from src.scrapers.discount import Discount
from src.app.main import app


class TestPercentageFormat(unittest.TestCase):
    """Test cases for discount percentage format."""
    
    def test_bergfreunde_percentage_format(self):
        """Test that BergfreundeScraper returns numeric percentage values."""
        scraper = BergfreundeScraper()
        
        # Test various input formats
        test_cases = [
            ("15%", "-15"),
            ("15 %", "-15"),
            ("15", "-15"),
            ("-15%", "-15"),
            ("15%%", "-15"),
            ("15 %%", "-15"),
            ("&&15%", "-15"),
            ("15&&", "-15"),
            ("from 15% to 20%", "-15"),
            ("", ""),
            (None, ""),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = scraper._clean_discount_percent(input_text)
                self.assertEqual(result, expected, 
                               f"Input '{input_text}' should return '{expected}', got '{result}'")
    
    def test_mountex_percentage_format(self):
        """Test that MountexScraper returns numeric percentage values."""
        scraper = MountexScraper()
        
        # Test various input formats
        test_cases = [
            ("15%", "-15"),
            ("15 %", "-15"),
            ("15", "-15"),
            ("-15%", "-15"),
            ("15%%", "-15"),
            ("15 %%", "-15"),
            ("&&15%", "-15"),
            ("15&&", "-15"),
            ("", ""),
            (None, ""),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = scraper._clean_discount_percent(input_text)
                self.assertEqual(result, expected, 
                               f"Input '{input_text}' should return '{expected}', got '{result}'")
    
    def test_fourcamping_percentage_format(self):
        """Test that FourCampingScraper returns numeric percentage values."""
        scraper = FourCampingScraper()
        
        # Test various input formats
        test_cases = [
            ("15%", "-15"),
            ("15 %", "-15"),
            ("15", "-15"),
            ("-15%", "-15"),
            ("15%%", "-15"),
            ("15 %%", "-15"),
            ("&&15%", "-15"),
            ("15&&", "-15"),
            ("", ""),
            (None, ""),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = scraper._clean_discount_percent(input_text)
                self.assertEqual(result, expected, 
                               f"Input '{input_text}' should return '{expected}', got '{result}'")
    
    def test_discount_object_format(self):
        """Test that Discount objects have properly formatted percentage values."""
        # Create a test discount with numeric percentage
        discount = Discount(
            product="Test Product",
            url="https://example.com",
            image_url="https://example.com/image.jpg",
            old_price="100.00€",
            new_price="85.00€",
            category="friends-nuts",
            site="Bergfreunde",
            discount_percent="-15"
        )
        
        # Test to_dict method
        discount_dict = discount.to_dict()
        self.assertEqual(discount_dict['discount_percent'], "-15")
        
        # Verify no % symbol in the discount_percent field
        self.assertNotIn('%', discount_dict['discount_percent'])
        
        # Verify it's a negative number as string
        self.assertTrue(discount_dict['discount_percent'].startswith('-'))
        self.assertTrue(discount_dict['discount_percent'][1:].isdigit())


class TestAPIEndpointFormat(unittest.TestCase):
    """Test cases for API endpoint response format."""
    
    def setUp(self):
        """Set up test client."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('src.services.discount_service.ALL_DISCOUNTS')
    def test_discounts_endpoint_response_format(self, mock_all_discounts):
        """Test that /discounts/<category> endpoint returns proper format."""
        # Mock discount data with numeric percentage values
        mock_discounts = [
            {
                'product': 'Test Product 1',
                'url': 'https://example.com/product1',
                'image_url': 'https://example.com/image1.jpg',
                'old_price': '100.00€',
                'new_price': '85.00€',
                'category': 'friends-nuts',
                'site': 'Bergfreunde',
                'discount_percent': '-15'
            },
            {
                'product': 'Test Product 2',
                'url': 'https://example.com/product2',
                'image_url': 'https://example.com/image2.jpg',
                'old_price': '50.00€',
                'new_price': '40.00€',
                'category': 'friends-nuts',
                'site': 'Mountex',
                'discount_percent': '-20'
            }
        ]
        
        mock_all_discounts.get.return_value = mock_discounts
        
        # Make request to API endpoint
        response = self.client.get('/discounts/friends-nuts')
        
        # Verify response status
        self.assertEqual(response.status_code, 200)
        
        # Parse response JSON
        data = json.loads(response.data.decode('utf-8'))
        
        # Verify response structure
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        
        # Verify discount percentage format
        for discount in data:
            self.assertIn('discount_percent', discount)
            discount_percent = discount['discount_percent']
            
            # Should be a string starting with minus
            self.assertIsInstance(discount_percent, str)
            self.assertTrue(discount_percent.startswith('-'))
            
            # Should not contain % symbol
            self.assertNotIn('%', discount_percent)
            
            # Should be numeric after minus sign
            self.assertTrue(discount_percent[1:].isdigit())
    
    def test_nonexistent_category_returns_404(self):
        """Test that non-existent category returns 404."""
        response = self.client.get('/discounts/nonexistent-category')
        self.assertEqual(response.status_code, 404)
    
    def test_refresh_endpoint_removed(self):
        """Test that /refresh endpoint has been removed."""
        response = self.client.post('/refresh')
        self.assertEqual(response.status_code, 404)


class TestEndToEndPercentageWorkflow(unittest.TestCase):
    """End-to-end test for the complete percentage format workflow."""
    
    def test_percentage_workflow(self):
        """Test the complete workflow from scraping to API response."""
        # This test uses mocked data to simulate the full workflow
        
        # Step 1: Mock scraper extracting percentage (simulates scraping)
        scraper = BergfreundeScraper()
        
        # Test that scraped percentage is cleaned to numeric format
        scraped_percentage = scraper._clean_discount_percent("15%%")
        self.assertEqual(scraped_percentage, "-15")
        
        # Step 2: Create discount object
        discount = Discount(
            product="Test Climbing Gear",
            url="https://example.com/gear",
            image_url="https://example.com/gear.jpg",
            old_price="120.00€",
            new_price="102.00€",
            category="friends-nuts",
            site="Bergfreunde",
            discount_percent=scraped_percentage
        )
        
        # Step 3: Convert to dict (simulates service layer processing)
        discount_dict = discount.to_dict()
        
        # Verify the discount_percent is in correct format
        self.assertEqual(discount_dict['discount_percent'], "-15")
        self.assertNotIn('%', discount_dict['discount_percent'])
        
        # Step 4: Simulate frontend receiving this data
        # The frontend should add the % symbol for display
        frontend_display = discount_dict['discount_percent'] + '%' if discount_dict['discount_percent'] else ''
        
        # Verify final display format
        self.assertEqual(frontend_display, "-15%")
        
        print("✓ End-to-end percentage workflow test passed")
        print(f"  - Scraped input: '15%%' -> Cleaned: '{scraped_percentage}'")
        print(f"  - API response: '{discount_dict['discount_percent']}'")
        print(f"  - Frontend display: '{frontend_display}'")


def run_e2e_tests():
    """Run all E2E tests for percentage format."""
    print("Running E2E tests for discount percentage format...")
    print("=" * 60)
    
    try:
        # Test percentage cleaning functions
        print("Testing percentage cleaning functions...")
        
        scrapers = [
            ("BergfreundeScraper", BergfreundeScraper()),
            ("MountexScraper", MountexScraper()),
            ("FourCampingScraper", FourCampingScraper()),
        ]
        
        test_inputs = [
            ("15%%", "-15"),
            ("15 %%", "-15"),
            ("15&&", "-15"),
            ("15%", "-15"),
            ("from 15% to 20%", "-15"),
        ]
        
        for scraper_name, scraper in scrapers:
            print(f"  Testing {scraper_name}...")
            for input_text, expected in test_inputs:
                result = scraper._clean_discount_percent(input_text)
                assert result == expected, f"{scraper_name}: '{input_text}' -> '{result}' != '{expected}'"
            print(f"    ✓ {scraper_name} percentage cleaning works correctly")
        
        print("✓ All percentage cleaning functions work correctly")
        
        # Test discount object format
        print("Testing discount object format...")
        discount = Discount(
            product="Test Product",
            url="https://example.com",
            image_url="https://example.com/image.jpg",
            old_price="100.00€",
            new_price="85.00€",
            category="friends-nuts",
            site="Bergfreunde",
            discount_percent="-15"
        )
        
        discount_dict = discount.to_dict()
        assert discount_dict['discount_percent'] == "-15"
        assert '%' not in discount_dict['discount_percent']
        
        print("✓ Discount object format is correct")
        
        print("=" * 60)
        print("🎉 All E2E percentage format tests passed!")
        
    except Exception as e:
        print(f"❌ E2E test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    # Run E2E tests
    print("\n" + "="*60)
    run_e2e_tests()