import time
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from src.core.logging_config import logger
from src.scrapers.discount_scraper import DiscountScraper
from src.scrapers.discount import Discount

class MountexScraper(DiscountScraper):
    BASE_URL = "https://www.mountex.hu"
    
    def __init__(self, discount_urls=None):
        super().__init__(discount_urls)


    def extract_discounts_from_category(self, url):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        discounts = []
        
        # Get product items
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
                    category=None,  # Will be set by the service layer
                    discount_percent=discount_percent
                ))

        logger.info(f"[MountexScraper] Found {len(discounts)} discounts.")
        return discounts