import re
from decimal import Decimal, InvalidOperation

from app.data.print_sizes import PRINT_SIZES
from app.models.print_size import PrintSize


def normalize_print_size(value: str) -> str:
    cleaned = value.strip().upper()

    # Normalize A-series formats: "a4", "A 4", " A4 "
    a_size = re.fullmatch(r"A\s*(\d)\+?", cleaned)

    if a_size:
        number = a_size.group(1)

        if cleaned.replace(" ", "").endswith("+"):
            return f"A{number}+"

        return f"A{number}"

    # Normalize dimensions: ×, X and x all become x
    cleaned = cleaned.replace("×", "X")
    cleaned = re.sub(r"\s+", "", cleaned)
    cleaned = cleaned.removesuffix("CM")

    dimension_match = re.fullmatch(r"(\d+)X(\d+)", cleaned)

    if dimension_match:
        width, height = dimension_match.groups()
        return f"{width} × {height} cm"

    raise ValueError(f"Invalid print size format: {value}")

def get_supported_print_size(value: str) -> PrintSize:
    normalized = normalize_print_size(value)

    for print_size in PRINT_SIZES:
        if print_size.code == normalized:
            return print_size

    raise ValueError(f"Unsupported print size: {value}")



def clean_numeric_value(value: str | int | float | Decimal) -> Decimal:
    if isinstance(value, Decimal):
        result = value
    else:
        if isinstance(value, (int, float)):
            value = str(value)

        if not isinstance(value, str):
            raise ValueError("Value must be numeric or a numeric string.")

        cleaned = value.strip()
        cleaned = cleaned.replace("€", "").strip()

        try:
            result = Decimal(cleaned)
        except InvalidOperation as exc:
            raise ValueError(
                f"Cannot convert value to a number: {value}"
            ) from exc

    if not result.is_finite():
        raise ValueError(f"Value must be a finite number: {value}")

    return result
