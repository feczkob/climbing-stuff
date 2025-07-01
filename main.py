from scrapers.service import load_sites, CATEGORIES, SCRAPER_MAP, fetch_discounts_for_site_category

def print_discounts_category(category, site_name, discounts):
    if not discounts:
        return
    print(f"\n[{category}] Discounts found on {site_name}:")
    for discount in discounts:
        print(f"- {discount['product']}\n  URL: {discount['url']} \n  Image: {discount['image_url']}")

def main():
    sites = load_sites()
    categories = CATEGORIES  # This is a dict: {category: {site: url, ...}, ...}
    for category, urls in categories.items():
        for site in sites:
            site_name = site['name']
            if site_name not in urls or site_name not in SCRAPER_MAP:
                continue
            _, discounts = fetch_discounts_for_site_category(site_name, category, urls[site_name])
            print_discounts_category(category, site_name, discounts)

if __name__ == "__main__":
    main()