from typing import Optional

from pydantic import BaseModel


class Discount(BaseModel):
    product: str
    url: str
    image_url: str
    old_price: str
    new_price: str
    category: Optional[str] = None
    site: Optional[str] = None
    discount_percent: Optional[str] = None
