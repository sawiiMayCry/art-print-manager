from app.models.limited_edition import (
    EditionCopy,
    EditionCopyStatus,
    LimitedEdition,
)

ALLOWED_STATUS_TRANSITIONS = {
    EditionCopyStatus.AVAILABLE: {
        EditionCopyStatus.RESERVED,
        EditionCopyStatus.SOLD,
        EditionCopyStatus.RETIRED,
    },
    EditionCopyStatus.RESERVED: {
        EditionCopyStatus.AVAILABLE,
        EditionCopyStatus.SOLD,
        EditionCopyStatus.RETIRED,
    },
    EditionCopyStatus.SOLD: {
    EditionCopyStatus.AVAILABLE,
    EditionCopyStatus.RETIRED,
    },
    EditionCopyStatus.RETIRED: set(),
}


def create_edition_copies(
    limited_edition: LimitedEdition,
) -> list[EditionCopy]:
    return [
        EditionCopy(
            limited_edition_id=limited_edition.id,
            edition_number=number,
        )
        for number in range(1, limited_edition.edition_size + 1)
    ]

def validate_edition_copies(
    limited_edition: LimitedEdition,
    copies: list[EditionCopy],
) -> None:
    seen_numbers: set[int] = set()

    for copy in copies:
        if copy.limited_edition_id != limited_edition.id:
            raise ValueError(
                "Edition copy does not belong to this limited edition."
            )

        if copy.edition_number > limited_edition.edition_size:
            raise ValueError(
                f"Edition number {copy.edition_number} exceeds "
                f"edition size {limited_edition.edition_size}."
            )

        if copy.edition_number in seen_numbers:
            raise ValueError(
                f"Duplicate edition number: {copy.edition_number}."
            )

        seen_numbers.add(copy.edition_number)


def change_copy_status(
    copy: EditionCopy,
    new_status: EditionCopyStatus,
) -> EditionCopy:
    if new_status == copy.status:
        raise ValueError(
            f"Edition copy is already {copy.status.value}."
        )

    allowed_statuses = ALLOWED_STATUS_TRANSITIONS[copy.status]

    if new_status not in allowed_statuses:
        raise ValueError(
            f"Invalid status transition: "
            f"{copy.status.value} → {new_status.value}."
        )

    data = copy.model_dump()
    data["status"] = new_status

    return EditionCopy.model_validate(data)