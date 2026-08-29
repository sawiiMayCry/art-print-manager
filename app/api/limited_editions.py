from fastapi import APIRouter, HTTPException, status

from app.data.artworks import ARTWORKS
from app.data.limited_editions import EDITION_COPIES, LIMITED_EDITIONS
from app.models.artwork import EditionType
from app.models.limited_edition import (
    EditionCopy,
    EditionCopyStatus,
    EditionCopyStatusUpdate,
    EditionSummary,
    LimitedEdition,
    LimitedEditionInput,
)
from app.services.limited_editions import (
    change_copy_status,
    create_edition_copies,
    validate_edition_copies,
)


router = APIRouter(
    tags=["Limited Editions"],
)


def get_artwork(artwork_id: str):
    for artwork in ARTWORKS:
        if artwork.id == artwork_id:
            return artwork

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Artwork not found.",
    )


def get_limited_edition(artwork_id: str) -> LimitedEdition:
    for edition in LIMITED_EDITIONS:
        if edition.artwork_id == artwork_id:
            return edition

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Limited edition not found.",
    )


def build_edition_summary(
    edition: LimitedEdition,
) -> EditionSummary:
    copies = [copy for copy in EDITION_COPIES if copy.limited_edition_id == edition.id]

    return EditionSummary(
        id=edition.id,
        artwork_id=edition.artwork_id,
        edition_size=edition.edition_size,
        available=sum(copy.status == EditionCopyStatus.AVAILABLE for copy in copies),
        reserved=sum(copy.status == EditionCopyStatus.RESERVED for copy in copies),
        sold=sum(copy.status == EditionCopyStatus.SOLD for copy in copies),
        retired=sum(copy.status == EditionCopyStatus.RETIRED for copy in copies),
    )


@router.post(
    "/editions",
    response_model=LimitedEdition,
    status_code=status.HTTP_201_CREATED,
    summary="Create limited edition",
)
def create_limited_edition(
    edition_input: LimitedEditionInput,
) -> LimitedEdition:
    artwork = get_artwork(edition_input.artwork_id)

    if artwork.edition_type != EditionType.LIMITED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Artwork is not configured as a limited edition.",
        )

    for existing_edition in LIMITED_EDITIONS:
        if existing_edition.artwork_id == edition_input.artwork_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Limited edition already exists for this artwork.",
            )

    edition = LimitedEdition(
        **edition_input.model_dump(),
    )

    copies = create_edition_copies(edition)

    validate_edition_copies(
        edition,
        copies,
    )

    LIMITED_EDITIONS.append(edition)
    EDITION_COPIES.extend(copies)

    return edition


@router.get(
    "/editions/{artwork_id}",
    response_model=EditionSummary,
    summary="Get limited edition summary",
)
def get_edition_summary(
    artwork_id: str,
) -> EditionSummary:
    get_artwork(artwork_id)

    edition = get_limited_edition(artwork_id)

    return build_edition_summary(edition)


@router.get(
    "/editions/{artwork_id}/copies",
    response_model=list[EditionCopy],
    summary="List limited edition copies",
)
def get_edition_copies(
    artwork_id: str,
) -> list[EditionCopy]:
    get_artwork(artwork_id)

    edition = get_limited_edition(artwork_id)

    return [copy for copy in EDITION_COPIES if copy.limited_edition_id == edition.id]


@router.patch(
    "/edition-copies/{copy_id}/status",
    response_model=EditionCopy,
    summary="Update edition copy status",
)
def update_edition_copy_status(
    copy_id: str,
    status_update: EditionCopyStatusUpdate,
) -> EditionCopy:
    for index, copy in enumerate(EDITION_COPIES):
        if copy.id == copy_id:
            try:
                updated_copy = change_copy_status(
                    copy,
                    status_update.status,
                )
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=str(exc),
                ) from exc

            EDITION_COPIES[index] = updated_copy

            return updated_copy

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Edition copy not found.",
    )
