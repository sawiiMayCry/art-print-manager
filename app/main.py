from fastapi import FastAPI, status

from app.api.artworks import router as artworks_router
from app.api.print_sizes import router as print_sizes_router
from app.api.price_books import router as price_books_router
from app.api.print_products import router as print_products_router


app = FastAPI(
    title="Fine Art Print Manager",
    description="API for managing fine-art prints, pricing, products, and limited editions.",
    version="0.1.0",
)

app.include_router(artworks_router)
app.include_router(print_sizes_router)
app.include_router(price_books_router)
app.include_router(print_products_router)

@app.get(
    "/health",
    tags=["System"],
    summary="Check API health",
    status_code=status.HTTP_200_OK,
)
def health_check() -> dict[str, str]:
    return {"status": "ok"}