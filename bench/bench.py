"""Benchmarks for the Python implementation.

Runs the same cases as `src-rs/benches/compare.rs`, with the same method:
each case is calibrated so one sample takes about TARGET_SAMPLE_NS, then
SAMPLES samples are taken and the median time per operation is reported.

Usage (from the shopcart/ directory):

    python bench/bench.py [output.json]
"""
import json
import platform
import statistics
import sys
import time
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src-py"))

from cart import Cart  # noqa: E402
from currency import to_money  # noqa: E402
from pricing import apply_discount, compute_tax  # noqa: E402
from receipt import render_receipt  # noqa: E402

SIZES = (10, 100, 1000)
SAMPLES = 7
TARGET_SAMPLE_NS = 50_000_000
HUNDRED = Decimal(100)


def make_cart(n: int) -> Cart:
    """Build a cart with `n` distinct SKUs and varying prices/quantities."""
    cart = Cart()
    for i in range(n):
        cart.add_item(f"sku{i:05}", f"{i % 97}.{i % 100:02}", i % 5 + 1)
    return cart


def measure(fn) -> float:
    """Return the median nanoseconds per call of `fn`."""
    iterations = 1
    while True:
        start = time.perf_counter_ns()
        for _ in range(iterations):
            fn()
        elapsed = time.perf_counter_ns() - start
        if elapsed >= TARGET_SAMPLE_NS / 10:
            break
        iterations *= 2
    iterations = max(1, int(iterations * TARGET_SAMPLE_NS / max(elapsed, 1)))

    samples = []
    for _ in range(SAMPLES):
        start = time.perf_counter_ns()
        for _ in range(iterations):
            fn()
        samples.append((time.perf_counter_ns() - start) / iterations)
    return statistics.median(samples)


def cases():
    """Yield (name, zero-argument callable) for every benchmark case."""
    yield "to_money", lambda: to_money("1234.565")
    yield "apply_discount", lambda: apply_discount(HUNDRED, "WELCOME10")
    yield "compute_tax", lambda: compute_tax(HUNDRED, "DE")
    for n in SIZES:
        cart = make_cart(n)
        yield f"build_cart/{n}", lambda n=n: make_cart(n)
        yield f"subtotal/{n}", cart.subtotal
        yield f"total/{n}", lambda cart=cart: cart.total("DE", "WELCOME10")
        yield f"render_receipt/{n}", lambda cart=cart: render_receipt(cart, "DE", "WELCOME10")


def main() -> None:
    results = {}
    for name, fn in cases():
        results[name] = measure(fn)
        print(f"{name:<22}{results[name]:>14.1f} ns/op", file=sys.stderr)
    output = {
        "implementation": "python",
        "version": platform.python_implementation() + " " + platform.python_version(),
        "results_ns": results,
    }
    text = json.dumps(output, indent=2)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
