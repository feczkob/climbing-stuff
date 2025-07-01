import requests
from bs4 import BeautifulSoup
from scrapers.discount_scraper import DiscountScraper

class FourcampingScraper(DiscountScraper):
    BASE_URL = "https://www.4camping.hu"

    def check_discounts(self):
        # Not used in this context
        pass

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

            # Extract name parts
            variant_tag = card.select_one(".product-card__heading-type")
            variant = variant_tag.get_text(strip=True) if variant_tag else ""
            producer = link_tag.select_one(".product-card__heading-producer")
            model = link_tag.select_one(".product-card__heading-model")
            if producer and model:
                base_name = f"{producer.get_text(strip=True)} {model.get_text(strip=True)}"
            else:
                base_name = link_tag.get_text(strip=True)

            # Compose product name with variant if present
            if variant:
                full_name = f"{variant} {base_name}"
            else:
                full_name = base_name

            img_tag = card.select_one(".product-card__thumbnail img")
            image_url = img_tag["src"] if img_tag else ""

            old_price = old_price_tag.get_text(strip=True)
            new_price_tag = card.select_one(".card-price__full strong")
            new_price = new_price_tag.get_text(strip=True) if new_price_tag else ""

            product = f"{full_name} {old_price} → {new_price}"

            discounts.append({
                "product": product,
                "url": product_url,
                "image_url": image_url
            })

        return discounts