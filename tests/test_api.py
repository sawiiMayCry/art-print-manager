import unittest

from fastapi.testclient import TestClient

from app.api.price_books import price_books
from app.api.print_products import print_products
from app.application import create_app
from app.data.artworks import ARTWORKS
from app.data.limited_editions import EDITION_COPIES, LIMITED_EDITIONS
from app.models.artwork import Artwork


class TestAPI(unittest.TestCase):
    def setUp(self):
        ARTWORKS.clear()
        price_books.clear()
        print_products.clear()
        LIMITED_EDITIONS.clear()
        EDITION_COPIES.clear()

        ARTWORKS.extend(
            [
                Artwork(
                    id="test-artwork-open",
                    title="Test Open Artwork",
                    year=2026,
                    status="ACTIVE",
                    edition_type="OPEN",
                ),
                Artwork(
                    id="test-artwork-limited",
                    title="Test Limited Artwork",
                    year=2026,
                    status="ACTIVE",
                    edition_type="LIMITED",
                ),
            ]
        )

        self.app = create_app(load_demo_data=False)
        self.client = TestClient(self.app)

    def tearDown(self):
        ARTWORKS.clear()
        price_books.clear()
        print_products.clear()
        LIMITED_EDITIONS.clear()
        EDITION_COPIES.clear()

    def test_health(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok"},
        )

    def test_list_artworks_uses_test_data(self):
        response = self.client.get("/artworks")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data), 2)
        self.assertEqual(
            data[0]["id"],
            "test-artwork-open",
        )

    def test_unknown_artwork_returns_404(self):
        response = self.client.get(
            "/artworks/does-not-exist"
        )

        self.assertEqual(response.status_code, 404)

    def test_print_sizes(self):
        response = self.client.get("/print-sizes/a4")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["code"],
            "A4",
        )

    def test_create_artwork(self):
        response = self.client.post(
            "/artworks",
            json={
                "id": "test-artwork-new",
                "title": "New Test Artwork",
                "year": 2026,
                "status": "ACTIVE",
                "edition_type": "OPEN",
            },
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.json()["id"],
            "test-artwork-new",
        )

    def test_update_artwork(self):
        response = self.client.put(
            "/artworks/test-artwork-open",
            json={
                "id": "test-artwork-open",
                "title": "Updated Test Artwork",
                "year": 2026,
                "status": "ACTIVE",
                "edition_type": "OPEN",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["title"],
            "Updated Test Artwork",
        )

    def test_no_price_book_configured(self):
        response = self.client.get("/price-books")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "No price book configured."},
        )

    def test_create_empty_price_book(self):
        response = self.client.post(
            "/price-books",
            json={
                "id": "test-price-book",
                "name": "Test Price Book",
                "currency": "EUR",
                "active": True,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()["prices"],
            [],
        )

    def test_add_user_specific_price(self):
        self.client.post(
            "/price-books",
            json={
                "id": "test-price-book",
                "name": "Test Price Book",
                "currency": "EUR",
                "active": True,
            },
        )

        response = self.client.post(
            "/price-books/test-price-book/prices",
            json={
                "print_size": "a4",
                "product_type": "print",
                "amount": "50.00",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()["product_type"],
            "PRINT",
        )

    def test_create_print_product(self):
        response = self.client.post(
            "/artworks/test-artwork-open/products",
            json={
                "print_size": "a4",
                "product_type": "framed",
                "active": True,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()["product_type"],
            "FRAMED",
        )

    def test_print_product_for_unknown_artwork_is_rejected(self):
        response = self.client.post(
            "/artworks/not-real/products",
            json={
                "print_size": "a4",
                "product_type": "PRINT",
                "active": True,
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_duplicate_print_product_is_rejected(self):
        payload = {
            "print_size": "a4",
            "product_type": "PRINT",
            "active": True,
        }

        self.client.post(
            "/artworks/test-artwork-open/products",
            json=payload,
        )

        response = self.client.post(
            "/artworks/test-artwork-open/products",
            json=payload,
        )

        self.assertEqual(response.status_code, 409)

    def test_create_limited_edition(self):
        response = self.client.post(
            "/editions",
            json={
                "artwork_id": "test-artwork-limited",
                "edition_size": 10,
            },
        )

        self.assertEqual(response.status_code, 201)

        copies_response = self.client.get(
            "/editions/test-artwork-limited/copies"
        )

        self.assertEqual(
            len(copies_response.json()),
            10,
        )

    def test_open_artwork_cannot_have_limited_edition(self):
        response = self.client.post(
            "/editions",
            json={
                "artwork_id": "test-artwork-open",
                "edition_size": 10,
            },
        )

        self.assertEqual(response.status_code, 409)

    def test_edition_copy_status_workflow(self):
        self.client.post(
            "/editions",
            json={
                "artwork_id": "test-artwork-limited",
                "edition_size": 10,
            },
        )

        copies = self.client.get(
            "/editions/test-artwork-limited/copies"
        ).json()

        copy_id = copies[0]["id"]

        reserve_response = self.client.patch(
            f"/edition-copies/{copy_id}/status",
            json={"status": "reserved"},
        )

        self.assertEqual(
            reserve_response.json()["status"],
            "RESERVED",
        )

        sell_response = self.client.patch(
            f"/edition-copies/{copy_id}/status",
            json={"status": "SOLD"},
        )

        self.assertEqual(
            sell_response.json()["status"],
            "SOLD",
        )

        duplicate_sale = self.client.patch(
            f"/edition-copies/{copy_id}/status",
            json={"status": "SOLD"},
        )

        self.assertEqual(
            duplicate_sale.status_code,
            409,
        )

    def test_limited_edition_summary_updates(self):
        self.client.post(
            "/editions",
            json={
                "artwork_id": "test-artwork-limited",
                "edition_size": 10,
            },
        )

        copies = self.client.get(
            "/editions/test-artwork-limited/copies"
        ).json()

        copy_id = copies[0]["id"]

        self.client.patch(
            f"/edition-copies/{copy_id}/status",
            json={"status": "SOLD"},
        )

        response = self.client.get(
            "/editions/test-artwork-limited"
        )

        summary = response.json()

        self.assertEqual(summary["edition_size"], 10)
        self.assertEqual(summary["available"], 9)
        self.assertEqual(summary["sold"], 1)

    def test_artwork_with_existing_edition_cannot_be_changed_to_open(self):
        self.client.post(
            "/editions",
            json={
                "artwork_id": "test-artwork-limited",
                "edition_size": 10,
            },
        )
    
        response = self.client.put(
            "/artworks/test-artwork-limited",
            json={
                "id": "test-artwork-limited",
                "title": "Test Limited Artwork",
                "year": 2026,
                "status": "ACTIVE",
                "edition_type": "OPEN",
            },
        )
    
        self.assertEqual(response.status_code, 409)

    def test_duplicate_price_book_id_is_rejected(self):
        payload = {
            "id": "test-price-book",
            "name": "Test Price Book",
            "currency": "EUR",
            "active": True,
        }

        self.client.post(
            "/price-books",
            json=payload,
        )

        response = self.client.post(
            "/price-books",
            json=payload,
        )

        self.assertEqual(response.status_code, 409)


    def test_unknown_price_book_returns_404(self):
        response = self.client.get(
            "/price-books/not-a-real-book"
        )

        self.assertEqual(response.status_code, 404)

    def test_artwork_update_with_mismatched_id_is_rejected(self):
        response = self.client.put(
            "/artworks/test-artwork-open",
            json={
                "id": "different-id",
                "title": "Test Artwork",
                "year": 2026,
                "status": "ACTIVE",
                "edition_type": "OPEN",
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_edition_status_is_rejected(self):
        self.client.post(
            "/editions",
            json={
                "artwork_id": "test-artwork-limited",
                "edition_size": 10,
            },
        )

        copies = self.client.get(
            "/editions/test-artwork-limited/copies"
        ).json()

        copy_id = copies[0]["id"]

        response = self.client.patch(
            f"/edition-copies/{copy_id}/status",
            json={
                "status": "BANANA",
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_delete_unknown_print_product_returns_404(self):
        response = self.client.delete(
            "/artworks/test-artwork-open/products/not-real"
        )

        self.assertEqual(response.status_code, 404)

    def test_product_cannot_be_deleted_through_wrong_artwork(self):
        create_response = self.client.post(
            "/artworks/test-artwork-open/products",
            json={
                "print_size": "a4",
                "product_type": "PRINT",
                "active": True,
            },
        )

        product_id = create_response.json()["id"]

        response = self.client.delete(
            f"/artworks/test-artwork-limited/products/{product_id}"
        )

        self.assertEqual(response.status_code, 404)

        products = self.client.get(
            "/artworks/test-artwork-open/products"
        ).json()

        self.assertEqual(len(products), 1)
        self.assertEqual(
            products[0]["id"],
            product_id,
        )


        
