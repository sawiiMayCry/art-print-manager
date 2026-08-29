import unittest

from pydantic import ValidationError

from app.models.limited_edition import (
    EditionCopy,
    EditionCopyStatus,
    LimitedEdition,
)
from app.services.limited_editions import (
    change_copy_status,
    create_edition_copies,
    validate_edition_copies,
)


class TestLimitedEditions(unittest.TestCase):
    def test_create_edition_copies(self):
        edition = LimitedEdition(
            artwork_id="test-artwork-001",
            edition_size=10,
        )

        copies = create_edition_copies(edition)

        self.assertEqual(len(copies), 10)
        self.assertEqual(copies[0].edition_number, 1)
        self.assertEqual(copies[-1].edition_number, 10)

    def test_zero_edition_number_is_rejected(self):
        with self.assertRaises(ValidationError):
            EditionCopy(
                limited_edition_id="test-edition",
                edition_number=0,
            )

    def test_number_above_edition_size_is_rejected(self):
        edition = LimitedEdition(
            artwork_id="test-artwork-001",
            edition_size=10,
        )

        copy = EditionCopy(
            limited_edition_id=edition.id,
            edition_number=11,
        )

        with self.assertRaises(ValueError):
            validate_edition_copies(edition, [copy])

    def test_duplicate_numbers_are_rejected(self):
        edition = LimitedEdition(
            artwork_id="test-artwork-001",
            edition_size=10,
        )

        copies = [
            EditionCopy(
                limited_edition_id=edition.id,
                edition_number=3,
            ),
            EditionCopy(
                limited_edition_id=edition.id,
                edition_number=3,
            ),
        ]

        with self.assertRaises(ValueError):
            validate_edition_copies(edition, copies)

    def test_retired_copy_cannot_become_available(self):
        copy = EditionCopy(
            limited_edition_id="test-edition",
            edition_number=1,
            status=EditionCopyStatus.RETIRED,
        )

        with self.assertRaises(ValueError):
            change_copy_status(
                copy,
                EditionCopyStatus.AVAILABLE,
            )

    def test_sold_copy_cannot_be_sold_twice(self):
        copy = EditionCopy(
            limited_edition_id="test-edition",
            edition_number=1,
        )

        copy = change_copy_status(
            copy,
            EditionCopyStatus.SOLD,
        )

        with self.assertRaises(ValueError):
            change_copy_status(
                copy,
                EditionCopyStatus.SOLD,
            )

    def test_sold_copy_can_be_returned(self):
        copy = EditionCopy(
            limited_edition_id="test-edition",
            edition_number=1,
        )

        copy = change_copy_status(
            copy,
            EditionCopyStatus.SOLD,
        )

        copy = change_copy_status(
            copy,
            EditionCopyStatus.AVAILABLE,
        )

        self.assertEqual(
            copy.status,
            EditionCopyStatus.AVAILABLE,
        )

    def test_edition_size_one_is_valid(self):
        edition = LimitedEdition(
            artwork_id="test-artwork-001",
            edition_size=1,
        )
    
        copies = create_edition_copies(edition)
    
        self.assertEqual(len(copies), 1)
        self.assertEqual(copies[0].edition_number, 1)
    
    
    def test_zero_edition_size_is_rejected(self):
        with self.assertRaises(ValidationError):
            LimitedEdition(
                artwork_id="test-artwork-001",
                edition_size=0,
            )
    
    
    def test_copy_from_wrong_edition_is_rejected(self):
        edition_a = LimitedEdition(
            artwork_id="test-artwork-a",
            edition_size=10,
        )
    
        edition_b = LimitedEdition(
            artwork_id="test-artwork-b",
            edition_size=10,
        )
    
        copy = EditionCopy(
            limited_edition_id=edition_a.id,
            edition_number=1,
        )
    
        with self.assertRaises(ValueError):
            validate_edition_copies(
                edition_b,
                [copy],
            )
    
    
    def test_status_input_is_normalized(self):
        copy = EditionCopy(
            limited_edition_id="test-edition",
            edition_number=1,
            status=" available ",
        )
    
        self.assertEqual(
            copy.status,
            EditionCopyStatus.AVAILABLE,
        )


if __name__ == "__main__":
    unittest.main()