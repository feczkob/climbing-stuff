import yaml
import importlib

with open('config/sites.yaml') as f:
    config = yaml.safe_load(f)

def print_discounts(site_name, discounts):
    if not discounts:
        return
    print(f"\nDiscounts found on {site_name}:")
    for discount in discounts:
        # Expecting discount dict to have 'product' and 'url' keys
        print(f"- {discount['product']}\n  URL: {discount['url']}")

for site in config['sites']:
    if not site.get('enabled', True):
        continue
    scraper_module = f"scrapers.{site['name']}"
    scraper = importlib.import_module(scraper_module)
    discounts = scraper.check_discounts()
    print_discounts(site['name'], discounts) 