from enum import Enum


class ProductType(str, Enum):
    PRINT = "PRINT"
    FRAMED = "FRAMED"