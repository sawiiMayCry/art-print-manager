import unittest

from pydantic import ValidationError
from datetime import datetime

from app.models.artwork import Artwork


class TestArtwork(unittest.TestCase):
    def test_create_valid_artwork(self):
        artwork = Artwork(
            id="test-artwork-001",
            title="Test Landscape",
            year=2026,
            status="ACTIVE",
            edition_type="OPEN",
        )

        self.assertEqual(artwork.id, "test-artwork-001")
        self.assertEqual(artwork.title, "Test Landscape")
        self.assertIsNone(artwork.location)

    def test_empty_title_is_rejected(self):
        with self.assertRaises(ValidationError):
            Artwork(
                id="test-artwork-002",
                title="   ",
                year=2026,
                status="ACTIVE",
                edition_type="OPEN",
            )

    def test_title_whitespace_is_trimmed(self):
        artwork = Artwork(
            id="test-artwork-003",
            title="   Test Artwork   ",
            year=2026,
            status="ACTIVE",
            edition_type="OPEN",
        )

        self.assertEqual(artwork.title, "Test Artwork")

    def test_future_year_is_rejected(self):
        with self.assertRaises(ValidationError):
            Artwork(
                id="test-artwork-004",
                title="Future Artwork",
                year=datetime.now().year + 1,
                status="ACTIVE",
                edition_type="OPEN",
            )

    def test_invalid_artwork_status_is_rejected(self):
        with self.assertRaises(ValidationError):
            Artwork(
                id="test-artwork-005",
                title="Test Artwork",
                year=2026,
                status="BANANA",
                edition_type="OPEN",
            )

    def test_invalid_edition_type_is_rejected(self):
        with self.assertRaises(ValidationError):
            Artwork(
                id="test-artwork-006",
                title="Test Artwork",
                year=2026,
                status="ACTIVE",
                edition_type="SPECIAL",
            )


if __name__ == "__main__":
    unittest.main()