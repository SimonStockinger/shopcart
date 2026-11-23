//! Benchmarks for the Rust implementation.
//!
//! Runs the same cases as `bench/bench.py`, with the same method: each case
//! is calibrated so one sample takes about `TARGET_SAMPLE_NS`, then `SAMPLES`
//! samples are taken and the median time per operation is reported.
//!
//! Usage (from `src-rs/`):
//!
//! ```text
//! cargo bench --bench compare -- [output.json]
//! ```

use std::hint::black_box;
use std::time::Instant;

use shopcart::{Cart, Decimal, apply_discount, compute_tax, parse_money, render_receipt};

const SIZES: [usize; 3] = [10, 100, 1000];
const SAMPLES: usize = 7;
const TARGET_SAMPLE_NS: f64 = 50_000_000.0;

/// Build a cart with `n` distinct SKUs and varying prices/quantities.
fn make_cart(n: usize) -> Cart {
    let mut cart = Cart::new();
    for i in 0..n {
        let price = parse_money(&format!("{}.{:02}", i % 97, i % 100)).unwrap();
        cart.add_item(&format!("sku{i:05}"), price, (i % 5 + 1) as u32)
            .unwrap();
    }
    cart
}

/// Return the median nanoseconds per call of `f`.
fn measure<R>(mut f: impl FnMut() -> R) -> f64 {
    let mut iterations: u64 = 1;
    let elapsed = loop {
        let start = Instant::now();
        for _ in 0..iterations {
            black_box(f());
        }
        let elapsed = start.elapsed().as_nanos() as f64;
        if elapsed >= TARGET_SAMPLE_NS / 10.0 {
            break elapsed;
        }
        iterations *= 2;
    };
    let iterations = ((iterations as f64 * TARGET_SAMPLE_NS / elapsed.max(1.0)) as u64).max(1);

    let mut samples: Vec<f64> = (0..SAMPLES)
        .map(|_| {
            let start = Instant::now();
            for _ in 0..iterations {
                black_box(f());
            }
            start.elapsed().as_nanos() as f64 / iterations as f64
        })
        .collect();
    samples.sort_by(f64::total_cmp);
    samples[SAMPLES / 2]
}

fn main() {
    let mut results: Vec<(String, f64)> = Vec::new();
    let mut run = |name: String, ns: f64| {
        eprintln!("{name:<22}{ns:>14.1} ns/op");
        results.push((name, ns));
    };

    let hundred = Decimal::from(100);
    run(
        "to_money".into(),
        measure(|| parse_money(black_box("1234.565")).unwrap()),
    );
    run(
        "apply_discount".into(),
        measure(|| apply_discount(black_box(hundred), black_box(Some("WELCOME10"))).unwrap()),
    );
    run(
        "compute_tax".into(),
        measure(|| compute_tax(black_box(hundred), black_box("DE")).unwrap()),
    );
    for n in SIZES {
        let cart = make_cart(n);
        run(
            format!("build_cart/{n}"),
            measure(|| make_cart(black_box(n))),
        );
        run(
            format!("subtotal/{n}"),
            measure(|| black_box(&cart).subtotal()),
        );
        run(
            format!("total/{n}"),
            measure(|| black_box(&cart).total("DE", Some("WELCOME10")).unwrap()),
        );
        run(
            format!("render_receipt/{n}"),
            measure(|| render_receipt(black_box(&cart), "DE", Some("WELCOME10")).unwrap()),
        );
    }

    let entries: Vec<String> = results
        .iter()
        .map(|(name, ns)| format!("    \"{name}\": {ns}"))
        .collect();
    let json = format!(
        "{{\n  \"implementation\": \"rust\",\n  \"version\": \"bench profile (optimized)\",\n  \"results_ns\": {{\n{}\n  }}\n}}\n",
        entries.join(",\n")
    );
    // `cargo bench` passes `--bench`; the first other argument is the output path.
    match std::env::args().skip(1).find(|arg| !arg.starts_with("--")) {
        Some(path) => std::fs::write(path, json).unwrap(),
        None => print!("{json}"),
    }
}
