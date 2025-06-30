import yaml
from scrapers.bergfreunde import BergfreundeScraper
from scrapers.mountex import MountexScraper

SCRAPER_CLASS_MAP = {
    "bergfreunde": BergfreundeScraper,
    "mountex": MountexScraper,
}

def load_config():
    with open('config/sites.yaml') as f:
        sites = yaml.safe_load(f)
    with open('config/categories.yaml') as f:
        categories = yaml.safe_load(f)['categories']
    return sites, categories

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

def instantiate_scrapers(sites):
    scraper_instances = {}
    for site in sites['sites']:
        if not site.get('enabled', True):
            continue
        site_name = site['name']
        scraper_class = SCRAPER_CLASS_MAP[site_name]
        scraper_instances[site_name] = scraper_class()
    return scraper_instances

def main():
    sites, categories = load_config()
    scraper_instances = instantiate_scrapers(sites)

    for site_name, scraper in scraper_instances.items():
        discounts = scraper.check_discounts()
        print_discounts(site_name, discounts)

    for category, urls in categories.items():
        for site_name, scraper in scraper_instances.items():
            if site_name not in urls:
                continue
            discounts = scraper.extract_discounts_from_category(urls[site_name])
            print_discounts_category(category, site_name, discounts)

if __name__ == "__main__":
    main()