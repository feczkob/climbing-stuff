import yaml
import os
from typing import List, Dict, Any

from src.core.config import config
from src.core.logging_config import logger
from src.scrapers.bergfreunde import BergfreundeScraper
from src.scrapers.fourcamping import FourCampingScraper
from src.scrapers.mountex import MountexScraper
from src.scrapers.maszas import MaszasScraper
from src.core.content_loader import HttpContentLoader, MockContentLoader, PlaywrightContentLoader
from src.dto.discount_url import DiscountUrl


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
        
        urls_by_site = self.create_discount_urls_by_site()

        for site, scraper_class in self.SCRAPER_CLASSES.items():
            content_loader = None
            if config.is_production():
                logger.info("Running in PRODUCTION mode - using real scrapers")
                if site == "mountex":
                    content_loader = PlaywrightContentLoader()
                else:
                    content_loader = HttpContentLoader()
            else:
                logger.info("Running in DEVELOPMENT mode - using mock scrapers")
                content_loader = MockContentLoader()
            
            if content_loader:
                scraper_map[site] = scraper_class(content_loader, urls_by_site.get(site, []))
                logger.info(f"Initialized {site} scraper with {len(urls_by_site.get(site, []))} URLs")

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
                    if config.is_production():
                        # In production, use real URLs
                        urls = url if isinstance(url, list) else [url]
                        for single_url in urls:
                            discount_url = DiscountUrl(
                                category=category_name,
                                url=single_url
                            )
                            if site_name not in urls_by_site:
                                urls_by_site[site_name] = []
                            urls_by_site[site_name].append(discount_url)
                    else:
                        # In development, use mock URLs
                        discount_url = DiscountUrl(
                            category=category_name,
                            url=f"{site_name}://{category_name}"
                        )
                        if site_name not in urls_by_site:
                            urls_by_site[site_name] = []
                        urls_by_site[site_name].append(discount_url)
        
        return urls_by_site 