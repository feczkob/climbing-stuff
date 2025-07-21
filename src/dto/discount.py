from pydantic import BaseModel
from typing import Optional


class Discount(BaseModel):
    product: str
    url: str
    image_url: Optional[str]
    old_price: str
    new_price: str
    category: Optional[str] = None
    site: Optional[str] = None
    discount_percent: Optional[str] = None
