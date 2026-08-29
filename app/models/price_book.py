from decimal import Decimal
from enum import Enum
from typing import Self
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from app.data.print_sizes import PRINT_SIZES
from app.models.product_type import ProductType



class Currency(str, Enum):
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    CHF = "CHF"


VALID_PRINT_SIZE_IDS = {print_size.id for print_size in PRINT_SIZES}

class PriceEntryInput(BaseModel):
    print_size: str
    product_type: ProductType
    amount: Decimal

    @field_validator("print_size")
    @classmethod
    def validate_print_size(cls, value: str) -> str:
        value = value.strip().lower()

        if value not in VALID_PRINT_SIZE_IDS:
            raise ValueError(f"Unknown print size: {value}")

        return value

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("Price must be a finite number.")

        if value <= 0:
            raise ValueError("Price must be greater than zero.")

        return value

class PriceEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    print_size: str
    product_type: ProductType
    amount: Decimal

    @field_validator("print_size")
    @classmethod
    def validate_print_size(cls, value: str) -> str:
        value = value.strip().lower()

        if value not in VALID_PRINT_SIZE_IDS:
            raise ValueError(f"Unknown print size: {value}")

        return value

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("Price must be a finite number.")

        if value <= 0:
            raise ValueError("Price must be greater than zero.")

        return value


class PriceBook(BaseModel):
    id: str
    name: str
    currency: Currency
    active: bool = True
    prices: list[PriceEntry] = Field(default_factory=list)

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().upper()

        return value

    @model_validator(mode="after")
    def validate_unique_price_entries(self) -> Self:
        seen = set()

        for price in self.prices:
            key = (price.print_size, price.product_type)

            if key in seen:
                raise ValueError(
                    f"Duplicate price entry: "
                    f"{price.print_size} + {price.product_type.value}"
                )

            seen.add(key)

        return self

class PriceBookInput(BaseModel):
    id: str
    name: str
    currency: Currency
    active: bool = True

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().upper()

        return value
