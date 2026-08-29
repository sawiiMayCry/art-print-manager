import unittest

from pydantic import ValidationError
from decimal import Decimal

from app.models.price_book import PriceBook


class TestPriceBook(unittest.TestCase):
    def test_empty_price_book_is_valid(self):
        price_book = PriceBook(
            id="test-book",
            name="Test Price Book",
            currency="EUR",
        )

        self.assertEqual(price_book.prices, [])

    def test_custom_price_is_created(self):
        price_book = PriceBook(
            id="test-book",
            name="Test Price Book",
            currency="EUR",
            prices=[
                {
                    "print_size": "a4",
                    "product_type": "PRINT",
                    "amount": "50.00",
                }
            ],
        )

        self.assertEqual(len(price_book.prices), 1)

    def test_negative_price_is_rejected(self):
        with self.assertRaises(ValidationError):
            PriceBook(
                id="test-book",
                name="Test Price Book",
                currency="EUR",
                prices=[
                    {
                        "print_size": "a4",
                        "product_type": "PRINT",
                        "amount": "-50",
                    }
                ],
            )

    def test_unknown_print_size_is_rejected(self):
        with self.assertRaises(ValidationError):
            PriceBook(
                id="test-book",
                name="Test Price Book",
                currency="EUR",
                prices=[
                    {
                        "print_size": "a5",
                        "product_type": "PRINT",
                        "amount": "50",
                    }
                ],
            )

    def test_duplicate_prices_are_rejected(self):
        with self.assertRaises(ValidationError):
            PriceBook(
                id="test-book",
                name="Test Price Book",
                currency="EUR",
                prices=[
                    {
                        "print_size": "a4",
                        "product_type": "PRINT",
                        "amount": "50",
                    },
                    {
                        "print_size": "a4",
                        "product_type": "PRINT",
                        "amount": "60",
                    },
                ],
            )

    def test_zero_price_is_rejected(self):
        with self.assertRaises(ValidationError):
            PriceBook(
                id="zero-book",
                name="Zero Price Book",
                currency="EUR",
                prices=[
                    {
                        "print_size": "a4",
                        "product_type": "PRINT",
                        "amount": "0",
                    }
                ],
            )

    def test_unknown_currency_is_rejected(self):
        with self.assertRaises(ValidationError):
            PriceBook(
                id="currency-book",
                name="Currency Test",
                currency="BANANA",
            )


    def test_currency_is_normalized(self):
        price_book = PriceBook(
            id="currency-book",
            name="Currency Test",
            currency=" eur ",
        )

        self.assertEqual(
            price_book.currency.value,
            "EUR",
        )


    def test_product_type_is_normalized(self):
        price_book = PriceBook(
            id="product-type-book",
            name="Product Type Test",
            currency="EUR",
            prices=[
                {
                    "print_size": "a4",
                    "product_type": " FrAmEd ",
                    "amount": "50",
                }
            ],
        )

        self.assertEqual(
            price_book.prices[0].product_type.value,
            "FRAMED",
        )

    def test_non_finite_price_is_rejected(self):
        with self.assertRaises(ValidationError):
            PriceBook(
                id="infinite-book",
                name="Infinite Price Book",
                currency="EUR",
                prices=[
                    {
                        "print_size": "a4", 
                        "product_type": "PRINT",
                        "amount": "Infinity",
                    }
                ],
            )


    def test_small_positive_price_is_valid(self):
        price_book = PriceBook(
            id="small-price-book",
            name="Small Price Book",
            currency="EUR",
            prices=[
                {
                    "print_size": "a4",
                    "product_type": "PRINT",
                    "amount": "0.01",
                }
            ],
        )
    
        self.assertEqual(
            price_book.prices[0].amount,
            Decimal("0.01"),
        )

if __name__ == "__main__":
    unittest.main()