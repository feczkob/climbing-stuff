from scrapers.service import fetch_discounts_for_category, fetch_all_discounts

def print_discounts_category(category, discounts):
    """Print discounts for a specific category."""
    if not discounts:
        return
    
    print(f"\n[{category}] Discounts found:")
    for discount in discounts:
        print(f"- {discount['product']}")
        print(f"  Site: {discount['site']}")
        print(f"  URL: {discount['url']}")
        if discount.get('image_url'):
            print(f"  Image: {discount['image_url']}")
        print()

def main():
    """Main function to fetch and display all discounts."""
    print("Fetching all discounts...")
    
    # Option 1: Fetch all discounts at once
    all_discounts = fetch_all_discounts()
    
    for category, discounts in all_discounts.items():
        print_discounts_category(category, discounts)
    
    # Option 2: Fetch by category (uncomment to use this approach)
    # categories = ['friends-nuts', 'slings', 'ropes', 'carabiners-quickdraws']
    # for category in categories:
    #     discounts = fetch_discounts_for_category(category)
    #     print_discounts_category(category, discounts)

if __name__ == "__main__":
    main()