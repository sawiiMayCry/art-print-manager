from app.models.limited_edition import EditionCopy, LimitedEdition


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