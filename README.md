# shopcart

A small Python shopping cart library: add and remove products, apply discount codes, compute regional tax, and render a plain-text receipt. All amounts are `Decimal`s rounded to cents (half-up).

## Requirements

- Python 3.10 or newer (uses `X | None` type syntax)
- No third-party dependencies

## Project structure

```
shopcart/
├── src/
│   ├── currency.py   # to_money / format_money: Decimal conversion and formatting
│   ├── pricing.py    # discount codes and tax rates
│   ├── cart.py       # Cart and LineItem models
│   └── receipt.py    # plain-text receipt rendering
└── test/
    ├── test_money.py     # tests for currency
    ├── test_pricing.py
    ├── test_cart.py
    └── test_receipt.py
```

| Module | Contents |
| --- | --- |
| `currency` | `to_money(value)` converts int/float/str/Decimal to a 2-decimal `Decimal`; `format_money(value, currency="EUR")` returns e.g. `"12.50 EUR"`. |
| `pricing` | `apply_discount(subtotal, code=None)` and `compute_tax(amount, region)`. |
| `cart` | `Cart` with `add_item`, `remove_item`, `subtotal`, `total`; `LineItem` with `line_total`. |
| `receipt` | `render_receipt(cart, region, discount_code=None)`. |

## Usage

The modules import each other by top-level name, so `src/` must be on the import path:

```bash
PYTHONPATH=src python
```

```python
from cart import Cart
from receipt import render_receipt

cart = Cart()
cart.add_item("apple", "0.50", 4)
cart.add_item("bread", "2.25")

cart.subtotal()                 # Decimal('4.25')
cart.total("DE", "WELCOME10")   # Decimal('4.56')

print(render_receipt(cart, "DE", "WELCOME10"))
```

Output:

```
apple      x4   2.00 EUR
bread      x1   2.25 EUR
Subtotal       4.25 EUR
Discount       -0.42 EUR
Tax (DE)       0.73 EUR
Total          4.56 EUR
```

## Pricing rules

The discount is applied to the subtotal first; tax is then computed on the discounted amount. Codes and regions are case-insensitive. Unknown codes or regions raise `ValueError`.

| Discount code | Reduction |
| --- | --- |
| `WELCOME10` | 10% |
| `HALFOFF` | 50% |

| Region | Tax rate |
| --- | --- |
| `DE` | 19% |
| `FR` | 20% |
| `US` | 0% |

To add a code or region, extend `DISCOUNT_CODES` or `TAX_RATES` in `src/pricing.py` (keys in upper case).

## Running the tests

From the `shopcart/` directory:

```bash
PYTHONPATH=src python -m unittest discover -s test -t . -v
```
