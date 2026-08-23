import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.models.artwork import Artwork


router = APIRouter(
    prefix="/artworks",
    tags=["Artworks"],
)

DEMO_ARTWORKS_PATH = (
    Path(__file__).resolve().parents[2]
    / "demo_data"
    / "artworks.example.json"
)


def load_artworks() -> list[Artwork]:
    with DEMO_ARTWORKS_PATH.open(encoding="utf-8") as file:
        data = json.load(file)

    return [Artwork.model_validate(item) for item in data]


artworks = load_artworks()

@router.get(
    "",
    response_model=list[Artwork],
    summary="List artworks",
)
def get_artworks() -> list[Artwork]:
    return artworks

@router.get(
    "/{artwork_id}",
    response_model=Artwork,
    summary="Get artwork",
)
def get_artwork(artwork_id: str) -> Artwork:
    for artwork in artworks:
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
    for existing_artwork in artworks:
        if existing_artwork.id == artwork.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Artwork with this ID already exists.",
            )

    artworks.append(artwork)

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

    for index, artwork in enumerate(artworks):
        if artwork.id == artwork_id:
            artworks[index] = updated_artwork
            return updated_artwork

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Artwork not found.",
    )