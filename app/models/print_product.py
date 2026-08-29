from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from app.data.print_sizes import PRINT_SIZES
from app.models.product_type import ProductType

VALID_PRINT_SIZE_IDS = {print_size.id for print_size in PRINT_SIZES}


class PrintProductInput(BaseModel):
    print_size: str
    product_type: ProductType
    active: bool = True

    @field_validator("print_size")
    @classmethod
    def validate_print_size(cls, value: str) -> str:
        value = value.strip().lower()

        if value not in VALID_PRINT_SIZE_IDS:
            raise ValueError(f"Unknown print size: {value}")

        return value


class PrintProduct(PrintProductInput):
    id: str = Field(default_factory=lambda: str(uuid4()))
    artwork_id: str
