import yaml
from scrapers.bergfreunde import BergfreundeScraper
from scrapers.mountex import MountexScraper

SCRAPER_CLASS_MAP = {
    "bergfreunde": BergfreundeScraper,
    "mountex": MountexScraper,
}

with open('config/sites.yaml') as f:
    config = yaml.safe_load(f)

with open('config/categories.yaml') as f:
    categories = yaml.safe_load(f)['categories']

def print_discounts(site_name, discounts):
    if not discounts:
        return
    print(f"\nDiscounts found on {site_name}:")
    for discount in discounts:
        print(f"- {discount['product']}\n  URL: {discount['url']}")

def print_discounts_category(category, site_name, discounts):
    if not discounts:
        return
    print(f"\n[{category}] Discounts found on {site_name}:")
    for discount in discounts:
        print(f"- {discount['product']}\n  URL: {discount['url']}")

scraper_instances = {}

for site in config['sites']:
    if not site.get('enabled', True):
        continue
    site_name = site['name']
    scraper_class = SCRAPER_CLASS_MAP[site_name]
    scraper = scraper_class()
    scraper_instances[site_name] = scraper

    discounts = scraper.check_discounts()
    print_discounts(site_name, discounts)

for category, urls in categories.items():
    for site_name, scraper in scraper_instances.items():
        if site_name not in urls:
            continue
        discounts = scraper.extract_discounts_from_category(urls[site_name])
        print_discounts_category(category, site_name, discounts)