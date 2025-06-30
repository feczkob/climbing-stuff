import time
from urllib.parse import urljoin

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def check_discounts():
    url = "https://mountex.hu"
    options = Options()
    options.add_argument("--headless=new")  # Use new headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # Wait for JS to load content

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
        if discount_tag:
            discount_percent = discount_tag.text.strip()
            brand_elem = card.find('div', class_='font-bold font-lora')
            brand = brand_elem.text.strip() if brand_elem else ""
            product_name_elem = card.select('h2 div:not(.font-bold)')
            product_name = product_name_elem[0].text.strip() if product_name_elem else "Unknown Product"
            full_product_name = f"{brand} {product_name}" if brand else product_name
            product_link = card.find('a', href=True)
            product_url = f"{url}{product_link['href']}" if product_link else None
            original_price_elem = card.find('div', class_='originalPrice')
            discounted_price_elem = card.find('div', class_='inActionPrice')
            price_info = ""
            if original_price_elem and discounted_price_elem:
                original_price = original_price_elem.text.strip()
                discounted_price = discounted_price_elem.text.strip()
                price_info = f" - {discounted_price} (was {original_price})"
            if product_url:
                discounts.append({
                    'product': f"{full_product_name} ({discount_percent}){price_info}",
                    'url': product_url
                })

    selected_subcategory_discounts = check_selected_categories()
    return discounts + selected_subcategory_discounts

def check_selected_categories():
    urls = [
        "https://mountex.hu/sziklamaszas-hegymaszas?v=115",
        "https://mountex.hu/sziklamaszas-hegymaszas?v=110",
        "https://mountex.hu/sziklamaszas-hegymaszas?v=109",
        "https://mountex.hu/sziklamaszas-hegymaszas?v=107",
    ]
    all_discounts = []
    for url in urls:
        all_discounts.extend(extract_discounts_from_category(url))
    return all_discounts

def extract_discounts_from_category(url):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # Wait for JS to load content

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    discounts = []

    for product in soup.select("div.bg-white.rounded-16"):
        discount_tag = product.select_one("span.bg-brand-highlight")
        discount_percent = discount_tag.get_text(strip=True) if discount_tag else ""

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

        product_url = urljoin("https://mountex.hu", name_link["href"]) if name_link and name_link.has_attr("href") else None

        if orig_price and disc_price and product_url:
            discounts.append({
                "product": f"{brand} {product_name} ({discount_percent}) - {disc_price} (was {orig_price})",
                "url": product_url
            })
    return discounts