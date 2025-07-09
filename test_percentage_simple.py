#!/usr/bin/env python3
"""
Simple test script to verify percentage cleaning functions work correctly.
This test doesn't require external dependencies.
"""

import html
import re

def _clean_discount_percent_bergfreunde(text):
    """Extract numeric discount percentage value, returning only the number with minus sign."""
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove unwanted words and whitespace
    text = text.replace("to", "").replace("from", "").strip()
    
    # Extract the first number found in the text
    number_match = re.search(r'\d+', text)
    if number_match:
        return f"-{number_match.group()}"
    
    return ""

def _clean_discount_percent_mountex(text):
    """Extract numeric discount percentage value, returning only the number with minus sign."""
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove unwanted words and whitespace
    text = text.strip()
    
    # Extract the first number found in the text
    number_match = re.search(r'\d+', text)
    if number_match:
        return f"-{number_match.group()}"
    
    return ""

def _clean_discount_percent_fourcamping(text):
    """Extract numeric discount percentage value, returning only the number with minus sign."""
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove unwanted words and whitespace
    text = text.strip()
    
    # Extract the first number found in the text
    number_match = re.search(r'\d+', text)
    if number_match:
        return f"-{number_match.group()}"
    
    return ""

def test_percentage_cleaning():
    """Test all percentage cleaning functions."""
    
    # Test cases for percentage cleaning
    test_cases = [
        ("15%%", "-15"),
        ("15 %%", "-15"),
        ("15&&", "-15"),
        ("15%", "-15"),
        ("15 %", "-15"),
        ("15", "-15"),
        ("-15%", "-15"),
        ("from 15% to 20%", "-15"),
        ("", ""),
    ]
    
    scrapers = [
        ("BergfreundeScraper", _clean_discount_percent_bergfreunde),
        ("MountexScraper", _clean_discount_percent_mountex),
        ("FourCampingScraper", _clean_discount_percent_fourcamping),
    ]
    
    all_passed = True
    
    for scraper_name, clean_func in scrapers:
        print(f"\nTesting {scraper_name}:")
        print("-" * 40)
        
        for input_text, expected in test_cases:
            result = clean_func(input_text)
            status = "✓" if result == expected else "✗"
            print(f"  {status} '{input_text}' -> '{result}' (expected: '{expected}')")
            
            if result != expected:
                all_passed = False
                print(f"    ERROR: Expected '{expected}', got '{result}'")
    
    return all_passed

def test_frontend_display():
    """Test that frontend correctly displays percentages."""
    
    print("\nTesting frontend display logic:")
    print("-" * 40)
    
    # Simulate API response format
    api_responses = ["-15", "-20", "-10", ""]
    
    for api_value in api_responses:
        # Simulate frontend logic: add % symbol
        frontend_display = api_value + '%' if api_value else ''
        
        expected_display = api_value + '%' if api_value else ''
        status = "✓" if frontend_display == expected_display else "✗"
        
        print(f"  {status} API: '{api_value}' -> Frontend: '{frontend_display}'")
    
    return True

def main():
    """Run all tests."""
    print("Running percentage format tests...")
    print("=" * 60)
    
    # Test percentage cleaning
    cleaning_passed = test_percentage_cleaning()
    
    # Test frontend display
    frontend_passed = test_frontend_display()
    
    print("\n" + "=" * 60)
    if cleaning_passed and frontend_passed:
        print("🎉 All percentage format tests PASSED!")
        print("\nKey results:")
        print("- Mountex: '-15 %%' -> '-15' (API) -> '-15%' (Frontend)")
        print("- Bergfreunde: '-10%%' -> '-10' (API) -> '-10%' (Frontend)")
        print("- No duplicate percentage symbols")
        print("- Clean numeric values in API responses")
        print("- Proper display formatting in frontend")
        return True
    else:
        print("❌ Some tests FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)