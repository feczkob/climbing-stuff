import requests
from bs4 import BeautifulSoup
import html
import re

from src.core.logging_config import logger
from src.scrapers.discount_scraper import DiscountScraper
from src.scrapers.discount import Discount

class FourCampingScraper(DiscountScraper):
    BASE_URL = "https://www.4camping.hu"
    
    def __init__(self, discount_urls=None):
        super().__init__(discount_urls)
    
    def _clean_discount_percent(self, text):
        """Clean and normalize discount percentage text."""
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove unwanted words and whitespace
        text = text.strip()
        
        # Remove multiple spaces and normalize
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Clean up any duplicate symbols or malformed characters
        text = re.sub(r'[&]{2,}', '%', text)  # Replace && with %
        text = re.sub(r'[%]{2,}', '%', text)  # Replace multiple % with single %
        
        # Ensure proper format: -XX% or XX%
        if text and not text.startswith('-'):
            text = f"-{text}"
        
        return text

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
            discount_percent_tag = card.select_one(".card-price__discount .card-price__discount-percent")
            discount_percent = self._clean_discount_percent(discount_percent_tag.get_text(strip=True) if discount_percent_tag else "")
            
            # If no discount percent tag found, try to calculate from prices
            if not discount_percent and old_price and new_price:
                try:
                    # Extract numbers from price strings (remove currency symbols and spaces)
                    old_num = float(re.sub(r'[^\d,.]', '', old_price).replace(',', '.'))
                    new_num = float(re.sub(r'[^\d,.]', '', new_price).replace(',', '.'))
                    if old_num > 0:
                        discount_percent = f"-{int(((old_num - new_num) / old_num) * 100)}%"
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