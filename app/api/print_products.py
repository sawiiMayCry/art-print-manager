from fastapi import APIRouter, HTTPException, status

from app.data.artworks import ARTWORKS
from app.models.print_product import PrintProduct, PrintProductInput
from app.services.print_products import ensure_unique_product


router = APIRouter(
    prefix="/artworks",
    tags=["Print Products"],
)


print_products: list[PrintProduct] = []


def ensure_artwork_exists(artwork_id: str) -> None:
    for artwork in ARTWORKS:
        if artwork.id == artwork_id:
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Artwork not found.",
    )

@router.get(
    "/{artwork_id}/products",
    response_model=list[PrintProduct],
    summary="List artwork print products",
)
def get_print_products(artwork_id: str) -> list[PrintProduct]:
    ensure_artwork_exists(artwork_id)

    return [
        product
        for product in print_products
        if product.artwork_id == artwork_id
    ]

@router.post(
    "/{artwork_id}/products",
    response_model=PrintProduct,
    status_code=status.HTTP_201_CREATED,
    summary="Create artwork print product",
)
def create_print_product(
    artwork_id: str,
    product_input: PrintProductInput,
) -> PrintProduct:
    ensure_artwork_exists(artwork_id)

    try:
        ensure_unique_product(
            print_products,
            artwork_id,
            product_input,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    product = PrintProduct(
        artwork_id=artwork_id,
        **product_input.model_dump(),
    )

    print_products.append(product)

    return product

@router.delete(
    "/{artwork_id}/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete artwork print product",
)
def delete_print_product(
    artwork_id: str,
    product_id: str,
) -> None:
    ensure_artwork_exists(artwork_id)

    for index, product in enumerate(print_products):
        if (
            product.id == product_id
            and product.artwork_id == artwork_id
        ):
            del print_products[index]
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Print product not found.",
    )