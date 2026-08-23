from app.models.print_product import PrintProduct, PrintProductInput


def ensure_unique_product(
    products: list[PrintProduct],
    artwork_id: str,
    product_input: PrintProductInput,
) -> None:
    for product in products:
        if (
            product.artwork_id == artwork_id
            and product.print_size == product_input.print_size
            and product.product_type == product_input.product_type
        ):
            raise ValueError(
                "Product configuration already exists for "
                f"{product_input.print_size} + "
                f"{product_input.product_type.value}."
            )