import requests
from bs4 import BeautifulSoup

from src.core.logging_config import logger
from src.scrapers.discount_scraper import DiscountScraper
from src.scrapers.discount import Discount
import re

class FourCampingScraper(DiscountScraper):
    BASE_URL = "https://www.4camping.hu"
    
    def __init__(self, discount_urls=None):
        super().__init__(discount_urls)

    def extract_discounts_from_category(self, url):
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
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
            discount_tag = card.select_one(".card-price__discount .card-price__discount-percent")
            if discount_tag:
                raw_discount = discount_tag.get_text(strip=True).replace("%", "").strip()
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
                category=None,  # Will be set by the service layer
                discount_percent=discount_percent
            )
            discounts.append(discount)
        
        logger.info(f"[FourCampingScraper] Found {len(discounts)} discounts.")
        return discounts