import requests
from bs4 import BeautifulSoup

def check_discounts():
    url = "https://www.bergfreunde.eu/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    discounts = []
    # Find the main bargain section
    teaser = soup.find("div", class_="dyn-teaser ls-deal ls-teaser-main-two teasertype_lss")
    if not teaser:
        print("Bargain section not found.")
        return []

    for product in teaser.find_all("div", class_="product-container"):
        # Discount percent
        discount_tag = product.find("span", class_="special_discount_percent")
        discount_percent = discount_tag.text.strip() if discount_tag else ""

        # Brand
        brand = ""
        brand_tag = product.find("div", class_="manufacturer-title")
        if brand_tag:
            brand = brand_tag.text.strip()
        else:
            brand_img = product.find("img", class_="manufacturer-icon")
            if brand_img and brand_img.has_attr("title"):
                brand = brand_img["title"]

        # Product name
        name_tag = product.find("div", class_="product-title")
        product_name = name_tag.text.strip() if name_tag else "Unknown Product"

        # Prices
        orig_price_tag = product.find("span", class_="strike-price")
        orig_price = orig_price_tag.text.strip() if orig_price_tag else ""
        disc_price_tag = product.find("span", class_="price")
        disc_price = disc_price_tag.text.strip() if disc_price_tag else ""

        # Product URL
        link_tag = product.find("a", class_="teaser-full-link")
        product_url = link_tag["href"] if link_tag and link_tag.has_attr("href") else None

        if product_url:
            discounts.append({
                "product": f"{brand} {product_name} ({discount_percent}) - {disc_price} (was {orig_price})",
                "url": product_url
            })

    return discounts