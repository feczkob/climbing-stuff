from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from logging_config import logger


class BergfreundeScraper:
    def check_discounts(self):
        url = "https://www.bergfreunde.eu/"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        discounts = []
        teaser = soup.find("div", class_="dyn-teaser ls-deal ls-teaser-main-two teasertype_lss")
        if not teaser:
            print("Bargain section not found.")
            return []

        for product in teaser.find_all("div", class_="product-container"):
            discount_tag = product.find("span", class_="special_discount_percent")
            discount_percent = "-" + discount_tag.text.strip().replace("to", "").replace("from", "") if discount_tag else ""

            brand = ""
            brand_tag = product.find("div", class_="manufacturer-title")
            if brand_tag:
                brand = brand_tag.text.strip()
            else:
                brand_img = product.find("img", class_="manufacturer-icon")
                if brand_img and brand_img.has_attr("title"):
                    brand = brand_img["title"]

            name_tag = product.find("div", class_="product-title")
            product_name = name_tag.text.strip() if name_tag else "Unknown Product"

            if brand and not product_name.lower().startswith(brand.lower()):
                full_product_name = f"{brand} {product_name}"
            else:
                full_product_name = product_name

            orig_price_tag = product.find("span", class_="strike-price")
            orig_price = orig_price_tag.text.strip().replace("from ", "") if orig_price_tag else ""
            disc_price_tag = product.find("span", class_="price")
            disc_price = disc_price_tag.text.strip().replace("from ", "") if disc_price_tag else ""

            link_tag = product.find("a", class_="teaser-full-link")
            product_url = link_tag["href"] if link_tag and link_tag.has_attr("href") else None

            img_tag = product.find('img', class_='product-image')
            image_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else None

            if product_url:
                discounts.append({
                    "product": full_product_name,
                    "url": product_url,
                    "image_url": image_url,
                    "originalPrice": orig_price,
                    "discountedPrice": disc_price,
                    "site": "Bergfreunde"
                })

        return discounts

    def extract_discounts_from_category(self, url):
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        discounts = []

        for product in soup.select("li.product-item.product-fallback"):
            discount_tag = product.select_one("span.js-special-discount-percent")
            discount_percent = "-" + discount_tag.get_text(strip=True).replace("to", "").replace("from", "") if discount_tag else ""

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
                discounts.append({
                    "product": full_product_name,
                    "url": product_url,
                    "image_url": image_url,
                    "originalPrice": orig_price,
                    "discountedPrice": disc_price,
                    "site": "Bergfreunde"
                })

        logger.info(f"[BergfreundeScraper] Found {len(discounts)} discounts.")
        return discounts