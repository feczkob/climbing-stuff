import yaml
import importlib

with open('config/sites.yaml') as f:
    config = yaml.safe_load(f)

with open('config/categories.yaml') as f:
    categories = yaml.safe_load(f)['categories']

def print_discounts(site_name, discounts):
    if not discounts:
        return
    print(f"\nDiscounts found on {site_name}:")
    for discount in discounts:
        # Expecting discount dict to have 'product' and 'url' keys
        print(f"- {discount['product']}\n  URL: {discount['url']}")

def print_discounts_category(category, site_name, discounts):
    if not discounts:
        return
    print(f"\n[{category}] Discounts found on {site_name}:")
    for discount in discounts:
        print(f"- {discount['product']}\n  URL: {discount['url']}")


# for site in config['sites']:
#     if not site.get('enabled', True):
#         continue
#     scraper_module = f"scrapers.{site['name']}"
#     scraper = importlib.import_module(scraper_module)
#     discounts = scraper.check_discounts()
#     print_discounts(site['name'], discounts)

for site in config['sites']:
    if not site.get('enabled', True):
        continue
    site_name = site['name']
    scraper_module = f"scrapers.{site_name}"
    scraper = importlib.import_module(scraper_module)

    discounts = scraper.check_discounts()
    print_discounts(site['name'], discounts)

    for category, urls in categories.items():
        if site_name not in urls:
            continue
        discounts = scraper.extract_discounts_from_category(urls[site_name])
        print_discounts_category(category, site_name, discounts)