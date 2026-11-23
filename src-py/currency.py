"""Money helpers. All amounts are Decimals rounded to cents."""
from decimal import Decimal, ROUND_HALF_UP

#: Smallest currency unit; amounts are quantized to this precision.
CENT = Decimal("0.01")


def to_money(value) -> Decimal:
    """Convert an int, float, str or Decimal to a Decimal rounded to cents.

    Rounding is half-up (e.g. "2.675" -> 2.68). Floats are converted via
    `str()` first so that values like `0.1 + 0.2` round as expected.

    Args:
        value: The amount to convert.

    Returns:
        The amount as a Decimal with two decimal places.
    """
    if isinstance(value, float):
        value = str(value)
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def format_money(value, currency: str = "EUR") -> str:
    """Format an amount like '12.50 EUR'.

    Args:
        value: The amount to format; it is rounded with `to_money` first.
        currency: Currency code appended after the amount. Defaults to "EUR".
    """
    return f"{to_money(value)} {currency}"
