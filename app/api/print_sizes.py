from fastapi import APIRouter, HTTPException, status

from app.data.print_sizes import PRINT_SIZES
from app.models.print_size import PrintSize


router = APIRouter(
    prefix="/print-sizes",
    tags=["Print Sizes"],
)


@router.get(
    "",
    response_model=list[PrintSize],
    summary="List print sizes",
)
def get_print_sizes() -> list[PrintSize]:
    return PRINT_SIZES


@router.get(
    "/{size_id}",
    response_model=PrintSize,
    summary="Get print size",
)
def get_print_size(size_id: str) -> PrintSize:
    for print_size in PRINT_SIZES:
        if print_size.id == size_id:
            return print_size

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Print size not found.",
    )