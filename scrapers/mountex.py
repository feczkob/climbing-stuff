import time
from unicodedata import category
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from logging_config import logger
from scrapers.discount_scraper import DiscountScraper
from scrapers.discount_dto import Discount


class MountexScraper(DiscountScraper):
    def __init__(self, discount_urls=None):
        super().__init__(discount_urls)
        
    def check_discounts(self):
        url = "https://mountex.hu"
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        discounts = []
        container = soup.find('div', class_='w-full pl-[6px] pr-[6px] pb-[6px] flex justify-start items-stretch overflow-hidden')
        if not container:
            print("Discount container not found.")
            return []

        product_cards = container.find_all('div', id=lambda x: x and x.startswith('product-'), recursive=False)
        for card in product_cards:
            discount_tag = card.find('span', class_='bg-brand-highlight')
            discount_percent = discount_tag.text.strip().replace('%', '') if discount_tag else ""
            brand_elem = card.find('div', class_='font-bold font-lora')
            brand = brand_elem.text.strip() if brand_elem else ""
            product_name_elem = card.select('h2 div:not(.font-bold)')
            product_name = product_name_elem[0].text.strip() if product_name_elem else "Unknown Product"
            full_product_name = f"{brand} {product_name}" if brand else product_name
            product_link = card.find('a', href=True)
            product_url = f"{url}{product_link['href']}" if product_link else None
            img_tag = card.select_one('a[href] img')
            image_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else None
            original_price_elem = card.find('div', class_='originalPrice')
            discounted_price_elem = card.find('div', class_='inActionPrice')
            original_price = original_price_elem.text.strip() if original_price_elem else ""
            discounted_price = discounted_price_elem.text.strip() if discounted_price_elem else ""
            if product_url:
                discounts.append(Discount(
                    product=full_product_name,
                    url=product_url,
                    image_url=image_url,
                    original_price=original_price,
                    discounted_price=discounted_price,
                    site='Mountex',
                    discount_percent=discount_percent
                ))

        return discounts

    def extract_discounts_from_category(self, url):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        discounts = []
        products = soup.select("div.bg-white.rounded-16")
        
        for product in products:
            discount_tag = product.select_one("span.bg-brand-highlight")
            discount_percent = discount_tag.get_text(strip=True).replace(' %', '') if discount_tag else ""
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
                    original_price=orig_price,
                    discounted_price=disc_price,
                    site="Mountex",
                    discount_percent=discount_percent
                ))

        logger.info("[MountexScraper] Found %d discounts.", len(discounts))
        return discounts