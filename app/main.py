from fastapi import FastAPI, status

app = FastAPI(
    title="Fine Art Print Manager",
    description="API for managing fine-art prints, pricing, products, and limited editions.",
    version="0.1.0",
)


@app.get(
    "/health",
    tags=["System"],
    summary="Check API health",
    status_code=status.HTTP_200_OK,
)
def health_check() -> dict[str, str]:
    return {"status": "ok"}