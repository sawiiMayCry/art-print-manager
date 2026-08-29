from enum import Enum


class ProductType(str, Enum):
    PRINT = "PRINT"
    FRAMED = "FRAMED"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            normalized = value.strip().upper()

            for product_type in cls:
                if product_type.value == normalized:
                    return product_type

        return None
