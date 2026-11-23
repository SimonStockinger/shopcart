"""Plain-text receipt rendering."""
from cart import Cart
from currency import format_money
from pricing import apply_discount, compute_tax


def render_receipt(cart: Cart, region: str, discount_code: str | None = None) -> str:
    """Render a cart as a plain-text receipt.

    The receipt lists one line per item (sorted by SKU) with quantity and line
    total, followed by Subtotal, Discount (only if a code is given), Tax and
    Total lines. Example::

        apple      x4   2.00 EUR
        Subtotal       2.00 EUR
        Tax (DE)       0.38 EUR
        Total          2.38 EUR

    Args:
        cart: The cart to render.
        region: Tax region code (case-insensitive); shown upper case.
        discount_code: Optional discount code (case-insensitive).

    Returns:
        The receipt as a newline-separated string (no trailing newline).

    Raises:
        ValueError: If the region or discount code is unknown.
    """
    lines = []
    for item in sorted(cart.items.values(), key=lambda i: i.sku):
        lines.append(f"{item.sku:<10} x{item.quantity:<3} {format_money(item.line_total)}")
    subtotal = cart.subtotal()
    discounted = apply_discount(subtotal, discount_code)
    tax = compute_tax(discounted, region)
    tax_label = f"Tax ({region.upper()})"
    lines.append(f"{'Subtotal':<15}{format_money(subtotal)}")
    if discount_code:
        lines.append(f"{'Discount':<15}-{format_money(subtotal - discounted)}")
    lines.append(f"{tax_label:<15}{format_money(tax)}")
    lines.append(f"{'Total':<15}{format_money(discounted + tax)}")
    return "\n".join(lines)
