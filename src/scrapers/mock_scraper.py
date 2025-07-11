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
        self.site_name = self._get_site_name_from_urls()
        self.category_by_url = {url.url: url.category for url in self.discount_urls}

    def _get_site_name_from_urls(self) -> str:
        """Determine site name from the provided discount URLs."""
        if not self.discount_urls:
            return 'unknown'
        
        first_url = self.discount_urls[0].url
        if 'bergfreunde' in first_url:
            return 'bergfreunde'
        elif 'mountex' in first_url:
            return 'mountex'
        elif '4camping' in first_url:
            return '4camping'
        elif 'maszas' in first_url:
            return 'maszas'
        return 'unknown'

    def extract_discounts_from_category(self, url):
        """Extract discounts from a mock HTML file."""
        category = self.category_by_url.get(url)
        if not category:
            logger.warning(f"[MockScraper] Category not found for URL: {url}")
            return []

        mock_file_path = config.get_mock_file_path(self.site_name, category)
        
        if not os.path.exists(mock_file_path):
            logger.warning(f"[MockScraper] Mock file not found: {mock_file_path}")
            return []
        
        try:
            with open(mock_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Use the appropriate scraper logic based on the site
            if self.site_name == 'bergfreunde':
                return self._extract_bergfreunde_discounts(html_content, url)
            elif self.site_name == 'mountex':
                return self._extract_mountex_discounts(html_content, url)
            elif self.site_name == '4camping':
                return self._extract_4camping_discounts(html_content, url)
            elif self.site_name == 'maszas':
                return self._extract_maszas_discounts(html_content, url)
            else:
                logger.warning(f"[MockScraper] Unknown site for mock extraction: {self.site_name}")
                return []
                
        except Exception as e:
            logger.error(f"[MockScraper] Error reading mock file {mock_file_path}: {e}")
            return []
    
    def _extract_bergfreunde_discounts(self, html_content: str, url: str) -> List[Discount]:
        """Extract discounts from Bergfreunde HTML using the same logic as the real scraper."""
        from urllib.parse import urljoin
        
        soup = BeautifulSoup(html_content, "html.parser")
        discounts = []
        
        product_items = soup.select("li.product-item.product-fallback")
        
        for product in product_items:
            discount_tag = product.select_one("span.js-special-discount-percent")
            if discount_tag:
                original_text = discount_tag.get_text(strip=True)
                raw_discount = original_text.replace("to", "").replace("from", "").replace("%", "").strip()
                # Remove any leading minus signs, then add one
                raw_discount = raw_discount.lstrip('-')
                discount_percent = f"-{raw_discount}" if raw_discount else ""
                logger.debug(f"[MockScraper] Original: '{original_text}' -> Raw: '{raw_discount}' -> Final: '{discount_percent}'")
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
                raw_discount = discount_tag.get_text(strip=True).replace("%", "").strip()
                raw_discount = raw_discount.lstrip('-')
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
    
    def _extract_maszas_discounts(self, html_content: str, url: str) -> List[Discount]:
        """Extract discounts from Maszas HTML using the same logic as the real scraper."""
        from urllib.parse import urljoin
        import re
        
        soup = BeautifulSoup(html_content, "html.parser")
        discounts = []
        products = soup.select("div.product-snapshot.list_div_item")

        for product in products:
            name_tag = product.select_one("h2 a")
            name = name_tag.get_text(strip=True) if name_tag else ""

            original_price_tag = product.select_one("span.list_original")
            if not original_price_tag:
                continue

            original_price = original_price_tag.get_text(strip=True) if original_price_tag else None

            discounted_price_tag = product.select_one("span.list_special")
            discounted_price = discounted_price_tag.get_text(strip=True) if discounted_price_tag else None

            product_url_tag = product.select_one("a.img-thumbnail-link")
            product_url = urljoin("https://www.maszas.hu", product_url_tag["href"]) if product_url_tag and product_url_tag.has_attr("href") else None
            
            image_url_tag = product.select_one("a.img-thumbnail-link img")
            image_url = None
            if image_url_tag:
                image_src = image_url_tag.get("data-src") or image_url_tag.get("src")
                if image_src:
                    image_url = urljoin("https://www.maszas.hu", image_src)

            discount_percent = ""
            if original_price and discounted_price:
                try:
                    old_num = float(re.sub(r'[^0-9,.]', '', original_price).replace(',', '.'))
                    new_num = float(re.sub(r'[^0-9,.]', '', discounted_price).replace(',', '.'))
                    if old_num > 0:
                        calc_discount = str(int(((old_num - new_num) / old_num) * 100))
                        calc_discount = calc_discount.lstrip('-')
                        discount_percent = f"-{calc_discount}" if calc_discount else ""
                except (ValueError, ZeroDivisionError):
                    discount_percent = ""
            
            if not all([name, original_price, discounted_price, product_url]):
                logger.warning(f"Could not extract all details for a product on {url}")
                continue

            discounts.append(Discount(
                product=name,
                url=product_url,
                image_url=image_url,
                old_price=original_price,
                new_price=discounted_price,
                category=None,
                discount_percent=discount_percent,
            ))
        
        logger.info(f"[MockScraper] Found {len(discounts)} Maszas discounts from mock file.")
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
            if discount_percent_tag:
                raw_discount = discount_percent_tag.get_text(strip=True).replace("%", "").strip()
                raw_discount = raw_discount.lstrip('-')
                discount_percent = f"-{raw_discount}" if raw_discount else ""
            else:
                discount_percent = ""
            # If no discount percent tag found, try to calculate from prices
            if not discount_percent and old_price and new_price:
                try:
                    # Extract numbers from price strings (remove currency symbols and spaces)
                    old_num = float(re.sub(r'[^\d,.]', '', old_price).replace(',', '.'))
                    new_num = float(re.sub(r'[^\d,.]', '', new_price).replace(',', '.'))
                    if old_num > 0:
                        calc_discount = str(int(((old_num - new_num) / old_num) * 100))
                        calc_discount = calc_discount.lstrip('-')
                        discount_percent = f"-{calc_discount}" if calc_discount else ""
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