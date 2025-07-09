import yaml
import os
from typing import List, Dict, Any

from logging_config import logger
from scrapers.bergfreunde import BergfreundeScraper
from scrapers.fourcamping import FourCampingScraper
from scrapers.mountex import MountexScraper
from scrapers.discount_dto import DiscountUrl


class ScraperManager:
    """Manages scraper initialization and configuration."""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.config_dir = os.path.join(self.base_dir, 'config')
        self.categories_file = os.path.join(self.config_dir, 'categories.yaml')
        self.sites_file = os.path.join(self.config_dir, 'sites.yaml')
        
        self.scraper_map = {}
        self.scraper_classes = {
            'bergfreunde': BergfreundeScraper,
            'mountex': MountexScraper,
            '4camping': FourCampingScraper,
        }
    
    def load_categories(self) -> Dict[str, Any]:
        """Load categories configuration from YAML file."""
        with open(self.categories_file, 'r') as f:
            categories_yaml = yaml.safe_load(f)
        return categories_yaml['categories']
    
    def load_sites(self) -> List[Dict[str, Any]]:
        """Load sites configuration from YAML file."""
        with open(self.sites_file, 'r') as f:
            sites_yaml = yaml.safe_load(f)
        return [site for site in sites_yaml['sites'] if site.get('enabled', True)]
    
    def create_discount_urls_by_site(self) -> Dict[str, List[DiscountUrl]]:
        """Create DiscountUrl objects grouped by site from the categories configuration."""
        urls_by_site = {}
        categories = self.load_categories()
        sites = self.load_sites()
        
        for category_name, site_urls in categories.items():
            for site in sites:
                site_name = site['name']
                url = site_urls.get(site_name)
                if url and site_name in self.scraper_classes:
                    # Handle both single URLs and lists of URLs
                    urls = url if isinstance(url, list) else [url]
                    for single_url in urls:
                        discount_url = DiscountUrl(
                            category=category_name,
                            url=single_url
                        )
                        if site_name not in urls_by_site:
                            urls_by_site[site_name] = []
                        urls_by_site[site_name].append(discount_url)
        
        return urls_by_site
    
    def initialize_scrapers(self) -> Dict[str, Any]:
        """Initialize scrapers with their respective DiscountUrl objects."""
        urls_by_site = self.create_discount_urls_by_site()
        
        for site_name, urls in urls_by_site.items():
            if site_name in self.scraper_classes:
                self.scraper_map[site_name] = self.scraper_classes[site_name](urls)
                logger.info(f"Initialized {site_name} scraper with {len(urls)} URLs")
        
        return self.scraper_map
    
    def get_scrapers(self) -> Dict[str, Any]:
        """Get the initialized scrapers map."""
        if not self.scraper_map:
            self.initialize_scrapers()
        return self.scraper_map 