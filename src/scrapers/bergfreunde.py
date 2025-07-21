from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.core.logging_config import logger
from src.core.content_loader import ContentLoader
from src.scrapers.discount_scraper import DiscountScraper
from src.dto.discount import Discount

class BergfreundeScraper(DiscountScraper):
    BASE_URL = "https://www.bergfreunde.eu"
    
    def __init__(self, content_loader: ContentLoader, discount_urls=None):
        super().__init__(content_loader, discount_urls)

    def extract_discounts_from_soup(self, soup: BeautifulSoup, url: str):
        discounts = []

        # Get product items
        product_items = soup.select("li.product-item.product-fallback")

        for product in product_items:
            discount_tag = product.select_one("span.js-special-discount-percent")
            if discount_tag:
                raw_discount = discount_tag.get_text(strip=True).replace("to", "").replace("from", "").replace("%", "").strip()
                # Remove any leading minus signs, then add one
                raw_discount = raw_discount.lstrip('-')
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
                    category=None,  # Will be set by the service layer
                    discount_percent=discount_percent
                ))

        logger.info(f"[BergfreundeScraper] Found {len(discounts)} discounts.")
        return discounts