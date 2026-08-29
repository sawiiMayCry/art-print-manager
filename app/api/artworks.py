from fastapi import APIRouter, HTTPException, status

from app.data.artworks import ARTWORKS
from app.models.artwork import Artwork, EditionType
from app.services.limited_editions import has_limited_edition


router = APIRouter(
    prefix="/artworks",
    tags=["Artworks"],
)


@router.get(
    "",
    response_model=list[Artwork],
    summary="List artworks",
)
def get_artworks() -> list[Artwork]:
    return ARTWORKS


@router.get(
    "/{artwork_id}",
    response_model=Artwork,
    summary="Get artwork",
)
def get_artwork(artwork_id: str) -> Artwork:
    for artwork in ARTWORKS:
        if artwork.id == artwork_id:
            return artwork

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Artwork not found.",
    )


@router.post(
    "",
    response_model=Artwork,
    status_code=status.HTTP_201_CREATED,
    summary="Create artwork",
)
def create_artwork(artwork: Artwork) -> Artwork:
    for existing_artwork in ARTWORKS:
        if existing_artwork.id == artwork.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Artwork with this ID already exists.",
            )

    ARTWORKS.append(artwork)

    return artwork


@router.put(
    "/{artwork_id}",
    response_model=Artwork,
    summary="Update artwork",
)
def update_artwork(
    artwork_id: str,
    updated_artwork: Artwork,
) -> Artwork:
    if artwork_id != updated_artwork.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artwork ID in URL must match artwork ID in request body.",
        )

    for index, artwork in enumerate(ARTWORKS):
        if artwork.id == artwork_id:
            if (
                artwork.edition_type == EditionType.LIMITED
                and updated_artwork.edition_type == EditionType.OPEN
                and has_limited_edition(artwork_id)
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Artwork with an existing limited edition "
                        "cannot be changed to OPEN."
                    ),
                )

            ARTWORKS[index] = updated_artwork
            return updated_artwork

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Artwork not found.",
    )
