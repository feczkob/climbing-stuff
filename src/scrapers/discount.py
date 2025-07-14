from pydantic import BaseModel


class Discount(BaseModel):
    product: str
    url: str
    image_url: str
    old_price: str
    new_price: str
    category: str
    site: str
    discount_percent: str
