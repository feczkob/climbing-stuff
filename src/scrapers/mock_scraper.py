import os
from bs4 import BeautifulSoup
from typing import List

from src.core.logging_config import logger
from src.core.config import config
from src.scrapers.discount_scraper import DiscountScraper
from src.scrapers.discount import Discount

class MockScraper(DiscountScraper):
    """Mock scraper that reads HTML from saved files instead of making real requests."""
    BASE_URL = "https://www.4camping.hu"  # Needed for 4camping product_url construction
    
    def __init__(self, discount_urls=None):
        super().__init__(discount_urls)
        self.mock_files_dir = config.get_mock_files_dir()
    
    def extract_discounts_from_category(self, url):
        """Extract discounts from a mock HTML file."""
        # Determine which mock file to use based on the URL
        site_name = self._get_site_name_from_url(url)
        category = self._get_category_from_url(url)
        
        mock_file_path = config.get_mock_file_path(site_name, category)
        
        if not os.path.exists(mock_file_path):
            logger.warning(f"Mock file not found: {mock_file_path}")
            return []
        
        logger.info(f"[MockScraper] Reading from mock file: {mock_file_path}")
        
        try:
            with open(mock_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Use the appropriate scraper logic based on the site
            if site_name == 'bergfreunde':
                return self._extract_bergfreunde_discounts(html_content, url)
            elif site_name == 'mountex':
                return self._extract_mountex_discounts(html_content, url)
            elif site_name == '4camping':
                return self._extract_4camping_discounts(html_content, url)
            else:
                logger.warning(f"Unknown site for mock extraction: {site_name}")
                return []
                
        except Exception as e:
            logger.error(f"Error reading mock file {mock_file_path}: {e}")
            return []
    
    def _get_site_name_from_url(self, url: str) -> str:
        """Extract site name from URL."""
        if 'bergfreunde.eu' in url:
            return 'bergfreunde'
        elif 'mountex.hu' in url:
            return 'mountex'
        elif '4camping.hu' in url:
            return '4camping'
        else:
            return 'unknown'
    
    def _get_category_from_url(self, url: str) -> str:
        """Extract category from URL."""
        if 'climbing-ropes' in url:
            return 'ropes'
        elif 'camming-devices-friends' in url or 'nuts' in url:
            return 'friends-nuts'
        elif 'slings-cord' in url or 'hurkok-hevederek' in url:
            return 'slings'
        elif 'carabiners-quickdraws' in url or 'karabinerek-expresszek' in url:
            return 'carabiners-quickdraws'
        else:
            return 'unknown'
    
    def _extract_bergfreunde_discounts(self, html_content: str, url: str) -> List[Discount]:
        """Extract discounts from Bergfreunde HTML using the same logic as the real scraper."""
        from urllib.parse import urljoin
        
        soup = BeautifulSoup(html_content, "html.parser")
        discounts = []
        
        product_items = soup.select("li.product-item.product-fallback")
        
        for product in product_items:
            discount_tag = product.select_one("span.js-special-discount-percent")
            if discount_tag:
                raw_discount = discount_tag.get_text(strip=True).replace("to", "").replace("from", "").replace("%", "")
                discount_percent = f"-{raw_discount}" if raw_discount else ""
            else:
                discount_percent = ""

            brand_tag = product.select_one("div.manufacturer-title")
            brand = brand_tag.get_text(strip=True) if brand_tag else ""

            name_tag = product.select_one("div.product-title")
            product_name = " ".join(name_tag.stripped_strings) if name_tag else "Unknown Product"

            if brand and not product_name.lower().startswith(brand.lower()):
                full_product_name = f"{brand} {product_name}"
            else:
                full_product_name = product_name

            orig_price_tag = product.select_one("span.uvp")
            orig_price = orig_price_tag.get_text(strip=True).replace("from ", "") if orig_price_tag else ""
            disc_price_tag = product.select_one("span.price.high-light")
            disc_price = disc_price_tag.get_text(strip=True).replace("from ", "") if disc_price_tag else ""

            link_tag = product.select_one("a.product-link")
            product_url = urljoin(url, link_tag["href"]) if link_tag and link_tag.has_attr("href") else None

            img_tag = product.select_one('a.product-link img.product-image')
            image_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else None

            if orig_price and disc_price and product_url:
                discounts.append(Discount(
                    product=full_product_name,
                    url=product_url,
                    image_url=image_url,
                    old_price=orig_price,
                    new_price=disc_price,
                    category=None,
                    discount_percent=discount_percent
                ))

        logger.info(f"[MockScraper] Found {len(discounts)} Bergfreunde discounts from mock file.")
        return discounts
    
    def _extract_mountex_discounts(self, html_content: str, url: str) -> List[Discount]:
        """Extract discounts from Mountex HTML using the same logic as the real scraper."""
        from urllib.parse import urljoin
        
        soup = BeautifulSoup(html_content, "html.parser")
        discounts = []
        
        products = soup.select("div.bg-white.rounded-16")
        
        for product in products:
            discount_tag = product.select_one("span.bg-brand-highlight")
            if discount_tag:
                raw_discount = discount_tag.get_text(strip=True).replace("%", "")
                discount_percent = f"-{raw_discount}" if raw_discount else ""
            else:
                discount_percent = ""
                
            name_link = product.select_one("a.text-black.unstyled")
            brand = ""
            product_name = ""
            if name_link:
                brand_tag = name_link.select_one("div.font-bold.font-lora")
                brand = brand_tag.get_text(strip=True) if brand_tag else ""
                name_divs = name_link.find_all("div")
                if len(name_divs) > 1:
                    product_name = name_divs[1].get_text(strip=True)
                else:
                    product_name = name_link.get_text(strip=True)

            orig_price_tag = product.select_one("div.originalPrice")
            orig_price = orig_price_tag.get_text(strip=True) if orig_price_tag else ""
            disc_price_tag = product.select_one("div.inActionPrice")
            disc_price = disc_price_tag.get_text(strip=True) if disc_price_tag else ""

            img_tag = product.select_one('a[href] img')
            image_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else None

            product_url = urljoin("https://mountex.hu", name_link["href"]) if name_link and name_link.has_attr("href") else None

            if orig_price and disc_price and product_url:
                discounts.append(Discount(
                    product=f"{brand} {product_name}".strip(),
                    url=product_url,
                    image_url=image_url,
                    old_price=orig_price,
                    new_price=disc_price,
                    category=None,
                    discount_percent=discount_percent
                ))

        logger.info(f"[MockScraper] Found {len(discounts)} Mountex discounts from mock file.")
        return discounts
    
    def _extract_4camping_discounts(self, html_content: str, url: str) -> List[Discount]:
        """Extract discounts from 4Camping HTML using the same logic as the real scraper."""
        import re
        
        soup = BeautifulSoup(html_content, "html.parser")
        discounts = []
        
        for card in soup.select(".product-card__inner"):
            old_price_tag = card.select_one(".card-price__discount del")
            if not old_price_tag:
                continue

            link_tag = card.select_one(".product-card__heading-link")
            if not link_tag:
                continue
            product_url = self.BASE_URL + link_tag["href"]

            variant_tag = card.select_one(".product-card__heading-type")
            variant = variant_tag.get_text(strip=True) if variant_tag else ""
            producer = link_tag.select_one(".product-card__heading-producer")
            model = link_tag.select_one(".product-card__heading-model")
            if producer and model:
                base_name = f"{producer.get_text(strip=True)} {model.get_text(strip=True)}"
            else:
                base_name = link_tag.get_text(strip=True)

            if variant:
                full_name = f"{base_name} {variant}"
            else:
                full_name = base_name

            img_tag = card.select_one(".product-card__thumbnail img")
            image_url = img_tag["src"] if img_tag else ""

            old_price = old_price_tag.get_text(strip=True)
            new_price_tag = card.select_one(".card-price__full strong")
            new_price = new_price_tag.get_text(strip=True) if new_price_tag else ""

            # Extract discount percentage
            discount_percent_tag = card.select_one(".card-price__discount .card-price__discount-percent")
            discount_percent = discount_percent_tag.get_text(strip=True) if discount_percent_tag else ""
            
            # If no discount percent tag found, try to calculate from prices
            if not discount_percent and old_price and new_price:
                try:
                    # Extract numbers from price strings (remove currency symbols and spaces)
                    old_num = float(re.sub(r'[^\d,.]', '', old_price).replace(',', '.'))
                    new_num = float(re.sub(r'[^\d,.]', '', new_price).replace(',', '.'))
                    if old_num > 0:
                        discount_percent = f"-{int(((old_num - new_num) / old_num) * 100)}"
                except (ValueError, ZeroDivisionError):
                    discount_percent = ""

            discount = Discount(
                product=full_name,
                url=product_url,
                image_url=image_url,
                old_price=old_price,
                new_price=new_price,
                category=None,
                discount_percent=discount_percent
            )
            discounts.append(discount)
        
        logger.info(f"[MockScraper] Found {len(discounts)} 4Camping discounts from mock file.")
        return discounts 