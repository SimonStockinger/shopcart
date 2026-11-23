# shopcart

A small shopping cart library: add and remove products, apply discount codes, compute regional tax, and render a plain-text receipt. All amounts are decimals rounded to cents (half-up).

The project has two equivalent implementations with the same behaviour and the same test cases:

- **Python** in `src-py/` (tests in `test/`)
- **Rust** in `src-rs/` (a Cargo crate with its own tests)

Both are benchmarked against each other in [BENCHMARKS.md](BENCHMARKS.md).

All commands below are run from the repository root unless stated otherwise.

## Project structure

```
shopcart/
├── src-py/               # Python implementation
│   ├── currency.py       # to_money / format_money: Decimal conversion and formatting
│   ├── pricing.py        # discount codes and tax rates
│   ├── cart.py           # Cart and LineItem models
│   └── receipt.py        # plain-text receipt rendering
├── test/                 # Python tests (unittest)
│   ├── __init__.py       # puts src-py/ on the import path
│   ├── test_currency.py
│   ├── test_pricing.py
│   ├── test_cart.py
│   └── test_receipt.py
├── bench/                # benchmarks (see BENCHMARKS.md)
│   ├── bench.py          # Python benchmark harness
│   ├── compare.py        # combines results into BENCHMARKS.md
│   ├── charts.py         # renders the SVG charts used by compare.py
│   ├── charts/           # generated charts (speedup.svg, times.svg)
│   └── results/          # raw results (python.json, rust.json)
├── BENCHMARKS.md         # Python vs Rust benchmark report
└── src-rs/               # Rust implementation (Cargo crate "shopcart")
    ├── Cargo.toml
    ├── Cargo.lock
    ├── benches/
    │   └── compare.rs    # Rust benchmark harness
    ├── src/
    │   ├── lib.rs        # crate root, re-exports the public API
    │   ├── error.rs      # Error enum
    │   ├── currency.rs
    │   ├── pricing.rs
    │   ├── cart.rs
    │   └── receipt.rs
    └── tests/            # integration tests, one file per module
        ├── currency.rs
        ├── pricing.rs
        ├── cart.rs
        └── receipt.rs
```

## Pricing rules

These rules apply to both implementations.

The discount is applied to the subtotal first; tax is then computed on the discounted amount. Codes and regions are case-insensitive. An empty discount code means no discount.

| Discount code | Reduction |
| --- | --- |
| `WELCOME10` | 10% |
| `HALFOFF` | 50% |

| Region | Tax rate |
| --- | --- |
| `DE` | 19% |
| `FR` | 20% |
| `US` | 0% |

To add a code or region, extend `DISCOUNT_CODES` or `TAX_RATES` in `src-py/pricing.py` and `src-rs/src/pricing.rs` (keys in upper case).

Example receipt for 4 × apple at 0.50 and 1 × bread at 2.25, region `DE`, code `WELCOME10`:

```
apple      x4   2.00 EUR
bread      x1   2.25 EUR
Subtotal       4.25 EUR
Discount       -0.42 EUR
Tax (DE)       0.73 EUR
Total          4.56 EUR
```

## Python

### Requirements

- Python 3.10 or newer (uses `X | None` type syntax)
- No third-party dependencies

### API

| Module | Contents |
| --- | --- |
| `currency` | `to_money(value)` converts int/float/str/Decimal to a 2-decimal `Decimal`; `format_money(value, currency="EUR")` returns e.g. `"12.50 EUR"`. |
| `pricing` | `apply_discount(subtotal, code=None)` and `compute_tax(amount, region)`. |
| `cart` | `Cart` with `add_item`, `remove_item`, `subtotal`, `total`; `LineItem` with `line_total`. |
| `receipt` | `render_receipt(cart, region, discount_code=None)`. |

Unknown discount codes, unsupported regions and non-positive quantities raise `ValueError`; removing a SKU that is not in the cart raises `KeyError`.

### Usage

The modules import each other by top-level name, so `src-py/` must be on the import path:

```bash
PYTHONPATH=src-py python
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

### Running the tests

```bash
python -m unittest discover -s test -t . -v
```

`test/__init__.py` adds `src-py/` to the import path, so no `PYTHONPATH` is needed.

There is no Python linter configured in the project.

## Rust

### Requirements

- Rust 1.85 or newer (edition 2024)
- [`rust_decimal`](https://crates.io/crates/rust_decimal) for exact decimal arithmetic (fetched by Cargo)

### API

Everything is re-exported from the crate root, so `use shopcart::...` is enough.

| Module | Contents |
| --- | --- |
| `currency` | `to_money(Decimal)` rounds to cents; `parse_money(&str)` and `money_from_f64(f64)` convert other inputs; `format_money(value, currency)` returns e.g. `"12.50 EUR"`; `DEFAULT_CURRENCY` is `"EUR"`. |
| `pricing` | `apply_discount(subtotal, code: Option<&str>)` and `compute_tax(amount, region)`. |
| `cart` | `Cart` with `new`, `add_item`, `remove_item`, `subtotal`, `total`; `LineItem` with `line_total`. Items are stored in a `BTreeMap` keyed by SKU. |
| `receipt` | `render_receipt(&cart, region, discount_code: Option<&str>)`. |
| `error` | `Error` enum returned by all fallible functions. |

Differences from the Python version, following Rust conventions:

- Amounts are passed as `Decimal`. Text and floats are converted explicitly with `parse_money` / `money_from_f64` instead of being accepted everywhere.
- Optional arguments are `Option`s, and there are no default values: `add_item` always takes a quantity and `format_money` always takes a currency.
- Errors are returned as `Result<_, Error>` instead of raised: `InvalidAmount`, `InvalidQuantity` (quantity 0; quantities are `u32` so they can't be negative), `UnknownSku`, `UnknownDiscountCode` and `UnsupportedRegion`.

### Usage

```rust
use shopcart::{Cart, parse_money, render_receipt};

fn main() -> Result<(), shopcart::Error> {
    let mut cart = Cart::new();
    cart.add_item("apple", parse_money("0.50")?, 4)?;
    cart.add_item("bread", parse_money("2.25")?, 1)?;

    cart.subtotal();                     // 4.25
    cart.total("DE", Some("WELCOME10"))?; // 4.56

    println!("{}", render_receipt(&cart, "DE", Some("WELCOME10"))?);
    Ok(())
}
```

### Building, linting and testing

From the `src-rs/` directory:

```bash
cargo test                                   # integration tests and doc tests
cargo clippy --all-targets -- -D warnings    # lint
cargo fmt --check                            # formatting
cargo doc --no-deps --open                   # API documentation
```

Cargo can't build when the project path contains a `:` (it breaks `LD_LIBRARY_PATH` for build scripts). In that case, put the build output somewhere else:

```bash
CARGO_TARGET_DIR=/tmp/shopcart-target cargo test
```

## Benchmarks

`bench/bench.py` and `src-rs/benches/compare.rs` run the same cases (parsing, discount, tax, building a cart, subtotal, total and rendering a receipt, with 10, 100 and 1000 items) using the same method, and `bench/compare.py` combines the results. Rust is about 4–32× faster depending on the case; see [BENCHMARKS.md](BENCHMARKS.md) for the full results.

To run them again:

```bash
python bench/bench.py bench/results/python.json
(cd src-rs && cargo bench --bench compare -- "$PWD/../bench/results/rust.json")
python bench/compare.py bench/results/python.json bench/results/rust.json > BENCHMARKS.md
```
