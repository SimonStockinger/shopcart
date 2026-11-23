"""Combine the Python and Rust benchmark results into BENCHMARKS.md.

Usage (from the shopcart/ directory):

    python bench/compare.py bench/results/python.json bench/results/rust.json > BENCHMARKS.md

Also writes the charts to bench/charts/ (speedup.svg, times.svg).
"""
import json
import platform
import subprocess
import sys
from pathlib import Path

from charts import speedup_chart, times_chart

CHART_DIR = Path(__file__).resolve().parent / "charts"

DESCRIPTIONS = {
    "to_money": 'Parse `"1234.565"` and round to cents',
    "apply_discount": "Apply `WELCOME10` to 100",
    "compute_tax": "19% `DE` tax on 100",
    "build_cart": "Create a cart and add *n* distinct items",
    "subtotal": "Sum all line totals",
    "total": "Subtotal, discount and tax",
    "render_receipt": "Render the full text receipt",
}


def fmt_time(ns: float) -> str:
    """Format nanoseconds with a readable unit."""
    for unit, scale in (("ms", 1e6), ("µs", 1e3)):
        if ns >= scale:
            return f"{ns / scale:.2f} {unit}"
    return f"{ns:.1f} ns"


def command_output(*cmd: str) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def cpu_name() -> str:
    for line in command_output("lscpu").splitlines():
        if line.startswith("Model name:"):
            return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def main() -> None:
    python = json.loads(Path(sys.argv[1]).read_text())
    rust = json.loads(Path(sys.argv[2]).read_text())
    py_ns, rs_ns = python["results_ns"], rust["results_ns"]

    out = [
        "# Benchmarks: Python vs Rust",
        "",
        "Both implementations run the same cases with the same method: each case is "
        "calibrated so one sample takes about 50 ms, 7 samples are taken, and the "
        "**median time per operation** is reported. Lower is better; *speedup* is "
        "Python time ÷ Rust time.",
        "",
        "## Environment",
        "",
        f"- CPU: {cpu_name()}",
        f"- OS: {platform.system()} {platform.release()}",
        f"- Python: {python['version']}",
        f"- Rust: {command_output('rustc', '--version')}, {rust['version']}",
        "",
        "## Results",
        "",
        "| Case | n | Python | Rust | Speedup |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    speedups = {}
    for name, p in py_ns.items():
        r = rs_ns[name]
        case, _, n = name.partition("/")
        speedups[name] = p / r
        out.append(f"| `{case}` | {n or '–'} | {fmt_time(p)} | {fmt_time(r)} | **{p / r:.1f}×** |")

    CHART_DIR.mkdir(exist_ok=True)
    (CHART_DIR / "speedup.svg").write_text(speedup_chart(py_ns, rs_ns) + "\n")
    (CHART_DIR / "times.svg").write_text(times_chart(py_ns, rs_ns) + "\n")
    out += [
        "",
        "![Rust speedup over Python per case](bench/charts/speedup.svg)",
        "",
        "![Time per operation, Python vs Rust, log scale](bench/charts/times.svg)",
    ]

    out += ["", "### Cases", ""]
    out += [f"- `{case}`: {text}" for case, text in DESCRIPTIONS.items()]

    ordered = sorted(speedups.items(), key=lambda kv: kv[1])
    growth = {"Python": [], "Rust": []}
    for label, results in (("Python", py_ns), ("Rust", rs_ns)):
        for name, ns in results.items():
            case, _, n = name.partition("/")
            bigger = f"{case}/{int(n) * 10}" if n else None
            if bigger in results:
                growth[label].append(results[bigger] / ns)
    scaling = ", ".join(
        f"{label} {min(g):.0f}–{max(g):.0f}×" for label, g in growth.items() if g
    )
    out += [
        "",
        "## Summary",
        "",
        f"- Rust is faster in every case, from **{ordered[0][1]:.1f}×** (`{ordered[0][0]}`) "
        f"to **{ordered[-1][1]:.1f}×** (`{ordered[-1][0]}`).",
        "- The gap is largest for pure decimal arithmetic (`subtotal`, `total`) and "
        "smallest for cases dominated by string building and allocation "
        "(`build_cart`, `render_receipt`).",
        "- Both implementations scale roughly linearly with the number of items: "
        f"10× more items costs {scaling} more time.",
        "",
        "## Reproducing",
        "",
        "```bash",
        "# from shopcart/",
        "python bench/bench.py bench/results/python.json",
        "(cd src-rs && cargo bench --bench compare -- \"$PWD/../bench/results/rust.json\")",
        "python bench/compare.py bench/results/python.json bench/results/rust.json > BENCHMARKS.md",
        "```",
        "",
        "Results are from a single run on one machine; expect some variation between runs.",
    ]
    print("\n".join(out))


if __name__ == "__main__":
    main()
