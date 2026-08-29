import unittest
from decimal import Decimal

from app.services.normalization import (
    clean_numeric_value,
    get_supported_print_size,
    normalize_print_size,
)


class TestNormalization(unittest.TestCase):
    def test_normalize_a4_variants(self):
        for value in ["a4", "A 4", " A4 "]:
            with self.subTest(value=value):
                self.assertEqual(
                    normalize_print_size(value),
                    "A4",
                )

    def test_normalize_dimension_variants(self):
        for value in [
            "60x60",
            "60 x 60",
            "60×60",
            "60 X 60 cm",
        ]:
            with self.subTest(value=value):
                self.assertEqual(
                    normalize_print_size(value),
                    "60 × 60 cm",
                )

    def test_clean_numeric_values(self):
        self.assertEqual(
            clean_numeric_value("230 €"),
            Decimal("230"),
        )
        self.assertEqual(
            clean_numeric_value("230.00"),
            Decimal("230.00"),
        )

    def test_invalid_numeric_value_is_rejected(self):
        with self.assertRaises(ValueError):
            clean_numeric_value("banana")

    def test_non_finite_value_is_rejected(self):
        with self.assertRaises(ValueError):
            clean_numeric_value("NaN")

    def test_unknown_supported_size_is_rejected(self):
        with self.assertRaises(ValueError):
            get_supported_print_size("75x50")


if __name__ == "__main__":
    unittest.main()
