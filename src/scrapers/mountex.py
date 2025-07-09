import requests
from bs4 import BeautifulSoup

from src.core.logging_config import logger
from src.scrapers.discount_scraper import DiscountScraper
from src.scrapers.discount_dto import Discount
import re

class MountexScraper(DiscountScraper):
    BASE_URL = "https://www.mountex.hu"
    
    def __init__(self, discount_urls=None):
        super().__init__(discount_urls)

    def check_discounts(self):
        pass

    def extract_discounts_from_category(self, url):
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        discounts = []

        for card in soup.select(".product-list__item"):
            old_price_tag = card.select_one(".product-list__price--old")
            if not old_price_tag:
                continue

            link_tag = card.select_one(".product-list__link")
            if not link_tag:
                continue
            product_url = self.BASE_URL + link_tag["href"]

            name_tag = card.select_one(".product-list__title")
            full_name = name_tag.get_text(strip=True) if name_tag else ""

            img_tag = card.select_one(".product-list__image img")
            image_url = img_tag["src"] if img_tag else ""

            old_price = old_price_tag.get_text(strip=True)
            new_price_tag = card.select_one(".product-list__price--final")
            new_price = new_price_tag.get_text(strip=True) if new_price_tag else ""

            discount = Discount(
                product=full_name,
                url=product_url,
                image_url=image_url,
                old_price=old_price,
                new_price=new_price,
                category=None  # Will be set by the service layer
            )
            discounts.append(discount)
        
        logger.info(f"[MountexScraper] Found {len(discounts)} discounts.")
        return discounts