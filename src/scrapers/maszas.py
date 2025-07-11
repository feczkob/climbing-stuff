from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.core.logging_config import logger
from src.scrapers.discount_scraper import DiscountScraper
from src.scrapers.discount import Discount
import re

class MaszasScraper(DiscountScraper):
    BASE_URL = "https://www.maszas.hu"

    def __init__(self, discount_urls=None):
        super().__init__(discount_urls)

    def _get_discounts(self, soup, url):
        discounts = []
        products = soup.select("div.product-snapshot.list_div_item")

        for product in products:
            name_tag = product.select_one("h2 a")
            name = name_tag.get_text(strip=True) if name_tag else ""

            original_price_tag = product.select_one("span.list_original")
            original_price = original_price_tag.get_text(strip=True) if original_price_tag else None

            discounted_price_tag = product.select_one("span.list_special")
            discounted_price = discounted_price_tag.get_text(strip=True) if discounted_price_tag else None

            product_url_tag = product.select_one("a.img-thumbnail-link")
            product_url = urljoin(self.BASE_URL, product_url_tag["href"]) if product_url_tag and product_url_tag.has_attr("href") else None
            
            image_url_tag = product.select_one("a.img-thumbnail-link img")
            image_url = urljoin(self.BASE_URL, image_url_tag["src"]) if image_url_tag and image_url_tag.has_attr("src") else None

            discount_percent = ""
            if original_price and discounted_price:
                try:
                    old_num = float(re.sub(r'[^0-9,.]', '', original_price).replace(',', '.'))
                    new_num = float(re.sub(r'[^0-9,.]', '', discounted_price).replace(',', '.'))
                    if old_num > 0:
                        calc_discount = str(int(((old_num - new_num) / old_num) * 100))
                        calc_discount = calc_discount.lstrip('-')
                        discount_percent = f"-{calc_discount}%" if calc_discount else ""
                except (ValueError, ZeroDivisionError):
                    discount_percent = ""
            
            if not all([name, original_price, discounted_price, product_url, image_url]):
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
        return discounts