from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class ProductType(str, Enum):
    PRINT = "PRINT"
    FRAMED = "FRAMED"


class PriceEntry(BaseModel):
    print_size: str
    product_type: ProductType
    amount: Decimal


class PriceBook(BaseModel):
    id: str
    name: str
    currency: str
    active: bool = True
    prices: list[PriceEntry] = Field(default_factory=list)