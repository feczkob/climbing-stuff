import time
from selenium import webdriver
from bs4 import BeautifulSoup

def check_discounts():
    url = "https://mountex.hu"
    driver = webdriver.Chrome()  # Or use webdriver.Firefox()
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
    return discounts