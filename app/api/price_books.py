from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.models.price_book import (
    PriceBook,
    PriceBookInput,
    PriceEntry,
    PriceEntryInput,
)


router = APIRouter(
    prefix="/price-books",
    tags=["Price Books"],
)


class MessageResponse(BaseModel):
    message: str


price_books: list[PriceBook] = []

def get_price_book_index(price_book_id: str) -> int:
    for index, price_book in enumerate(price_books):
        if price_book.id == price_book_id:
            return index

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Price book not found.",
    )


def rebuild_price_book(
    price_book: PriceBook,
    prices: list[PriceEntry],
) -> PriceBook:
    data = price_book.model_dump()
    data["prices"] = [price.model_dump() for price in prices]

    return PriceBook.model_validate(data)

@router.get(
    "",
    response_model=list[PriceBook] | MessageResponse,
    summary="List price books",
)
def get_price_books() -> list[PriceBook] | MessageResponse:
    if not price_books:
        return MessageResponse(
            message="No price book configured."
        )

    return price_books

@router.post(
    "",
    response_model=PriceBook,
    status_code=status.HTTP_201_CREATED,
    summary="Create price book",
)
def create_price_book(
    price_book_input: PriceBookInput,
) -> PriceBook:
    for existing_price_book in price_books:
        if existing_price_book.id == price_book_input.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Price book with this ID already exists.",
            )

    price_book = PriceBook(
        **price_book_input.model_dump(),
    )

    price_books.append(price_book)

    return price_book

@router.get(
    "/{price_book_id}",
    response_model=PriceBook,
    summary="Get price book",
)
def get_price_book(price_book_id: str) -> PriceBook:
    index = get_price_book_index(price_book_id)
    return price_books[index]

@router.post(
    "/{price_book_id}/prices",
    response_model=PriceEntry,
    status_code=status.HTTP_201_CREATED,
    summary="Add price",
)
def add_price(
    price_book_id: str,
    price_input: PriceEntryInput,
) -> PriceEntry:
    book_index = get_price_book_index(price_book_id)
    price_book = price_books[book_index]

    for existing_price in price_book.prices:
        if (
            existing_price.print_size == price_input.print_size
            and existing_price.product_type == price_input.product_type
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Price entry already exists for this print size and product type.",
            )

    new_price = PriceEntry(**price_input.model_dump())

    updated_prices = [
        *price_book.prices,
        new_price,
    ]

    price_books[book_index] = rebuild_price_book(
        price_book,
        updated_prices,
    )

    return new_price

@router.put(
    "/{price_book_id}/prices/{price_id}",
    response_model=PriceEntry,
    summary="Update price",
)
def update_price(
    price_book_id: str,
    price_id: str,
    price_input: PriceEntryInput,
) -> PriceEntry:
    book_index = get_price_book_index(price_book_id)
    price_book = price_books[book_index]

    price_index = None

    for index, price in enumerate(price_book.prices):
        if price.id == price_id:
            price_index = index
            break

    if price_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price entry not found.",
        )

    for price in price_book.prices:
        if (
            price.id != price_id
            and price.print_size == price_input.print_size
            and price.product_type == price_input.product_type
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Price entry already exists for this print size and product type.",
            )

    updated_price = PriceEntry(
        id=price_id,
        **price_input.model_dump(),
    )

    updated_prices = list(price_book.prices)
    updated_prices[price_index] = updated_price

    price_books[book_index] = rebuild_price_book(
        price_book,
        updated_prices,
    )

    return updated_price

@router.delete(
    "/{price_book_id}/prices/{price_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete price",
)
def delete_price(
    price_book_id: str,
    price_id: str,
) -> None:
    book_index = get_price_book_index(price_book_id)
    price_book = price_books[book_index]

    updated_prices = [
        price
        for price in price_book.prices
        if price.id != price_id
    ]

    if len(updated_prices) == len(price_book.prices):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price entry not found.",
        )

    price_books[book_index] = rebuild_price_book(
        price_book,
        updated_prices,
    )