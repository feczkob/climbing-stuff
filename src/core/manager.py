import yaml
import os
from typing import List, Dict, Any

from src.core.logging_config import logger
from src.core.config import config
from src.scrapers.bergfreunde import BergfreundeScraper
from src.scrapers.fourcamping import FourCampingScraper
from src.scrapers.mountex import MountexScraper
from src.scrapers.maszas import MaszasScraper
from src.scrapers.mock_scraper import MockScraper
from src.scrapers.discount_url import DiscountUrl


def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ScraperManager:
    """Manages scraper initialization and configuration."""
    
    SCRAPER_CLASSES = {
        'bergfreunde': BergfreundeScraper,
        'mountex': MountexScraper,
        '4camping': FourCampingScraper,
        'maszas': MaszasScraper,
    }

    def __init__(self, config_path='config/categories.yaml'):
        self.config_path = config_path
        self.categories = self.load_categories()
        self.scraper_map = self._initialize_scrapers()

    def _initialize_scrapers(self) -> Dict[str, Any]:
        scraper_map = {}
        # Choose scraper classes based on production mode
        if config.is_production():
            scraper_classes = {
                'bergfreunde': BergfreundeScraper,
                'mountex': MountexScraper,
                '4camping': FourCampingScraper,
                'maszas': MaszasScraper,
            }
            logger.info("Running in PRODUCTION mode - using real scrapers")
        else:
            scraper_classes = {
                'bergfreunde': MockScraper,
                'mountex': MockScraper,
                '4camping': MockScraper,
                'maszas': MockScraper,
            }
            logger.info("Running in DEVELOPMENT mode - using mock scrapers")

        for site, scraper_class in scraper_classes.items():
            site_urls = []
            for cat, urls_by_site in self.categories.items():
                urls = urls_by_site.get(site)
                if urls:
                    if isinstance(urls, str):
                        urls = [urls]
                    for url in urls:
                        site_urls.append(DiscountUrl(category=cat, url=url))

            scraper_map[site] = scraper_class(site_urls)
            logger.info(f"Initialized {site} scraper with {len(site_urls)} URLs")
        return scraper_map

    def get_scrapers(self) -> Dict[str, Any]:
        """Get the initialized scrapers map."""
        return self.scraper_map

    def load_categories(self) -> Dict[str, Any]:
        """Load categories configuration from YAML file."""
        with open(self.config_path, 'r') as f:
            categories_yaml = yaml.safe_load(f)
        return categories_yaml['categories']
    
    def create_discount_urls_by_site(self) -> Dict[str, List[DiscountUrl]]:
        """Create DiscountUrl objects grouped by site from the categories configuration."""
        urls_by_site = {}
        categories = self.load_categories()
        available_sites = self.SCRAPER_CLASSES.keys()
        
        for category_name, site_urls in categories.items():
            for site_name in available_sites:
                url = site_urls.get(site_name)
                if url:
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
            if site_name in self.SCRAPER_CLASSES:
                self.scraper_map[site_name] = self.SCRAPER_CLASSES[site_name](urls)
                logger.info(f"Initialized {site_name} scraper with {len(urls)} URLs")
        
        return self.scraper_map 