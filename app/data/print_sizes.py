from app.models.print_size import PrintSize


PRINT_SIZES = [
    PrintSize(
        id="a4",
        code="A4",
        width_mm=210,
        height_mm=297,
    ),
    PrintSize(
        id="a3",
        code="A3",
        width_mm=297,
        height_mm=420,
    ),
    PrintSize(
        id="a3-plus",
        code="A3+",
        width_mm=329,
        height_mm=483,  # not universal, but common for photo prints
    ),
    PrintSize(
        id="a2",
        code="A2",
        width_mm=420,
        height_mm=594,
    ),
    PrintSize(
        id="60x60",
        code="60 × 60 cm",
        width_mm=600,
        height_mm=600,
    ),
    PrintSize(
        id="90x60",
        code="90 × 60 cm",
        width_mm=900,
        height_mm=600,
    ),
]
