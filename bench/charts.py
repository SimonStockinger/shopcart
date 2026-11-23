"""Render the benchmark comparison as standalone SVG charts (no dependencies).

Used by compare.py. Each SVG carries its own light and dark colours and
switches with the viewer's `prefers-color-scheme`.
"""
import math
from html import escape

FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"

STYLE = """
<style>
  .surface { fill: #fcfcfb; }
  .t1 { fill: #0b0b0b; } .t2 { fill: #52514e; } .mut { fill: #898781; }
  .grid { stroke: #e1e0d9; stroke-width: 1; }
  .link { stroke: #c9c8c1; stroke-width: 2; }
  .py { fill: #2a78d6; } .rs { fill: #eb6834; }
  .ring { stroke: #fcfcfb; stroke-width: 2; }
  @media (prefers-color-scheme: dark) {
    .surface { fill: #1a1a19; }
    .t1 { fill: #f0efec; } .t2 { fill: #c3c2b7; }
    .grid { stroke: #2c2c2a; }
    .link { stroke: #4a4a46; }
    .py { fill: #3987e5; } .rs { fill: #d95926; }
    .ring { stroke: #1a1a19; }
  }
  text { font-family: %s; }
</style>
""" % FONT


def ordered_names(results: dict) -> list[str]:
    """Group cases: single operations first, then each sized case by n."""
    singles = [n for n in results if "/" not in n]
    sized: dict[str, list[str]] = {}
    for name in results:
        if "/" in name:
            sized.setdefault(name.split("/")[0], []).append(name)
    for names in sized.values():
        names.sort(key=lambda n: int(n.split("/")[1]))
    return singles + [n for names in sized.values() for n in names]


def label(name: str) -> str:
    case, _, n = name.partition("/")
    return f"{case} · n={n}" if n else case


def fmt_time(ns: float) -> str:
    for unit, scale in (("ms", 1e6), ("µs", 1e3)):
        if ns >= scale:
            return f"{ns / scale:.3g} {unit}"
    return f"{ns:.3g} ns"


def svg_open(width: int, height: int, title: str, desc: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(desc)}</desc>',
        STYLE,
        f'<rect class="surface" width="{width}" height="{height}" rx="8"/>',
    ]


def bar_path(x0: float, y: float, length: float, height: float, r: float = 4) -> str:
    """Horizontal bar anchored at x0 with only the data end (right) rounded."""
    r = min(r, length, height / 2)
    x1 = x0 + length
    return (
        f"M{x0:.1f},{y:.1f} H{x1 - r:.1f} Q{x1:.1f},{y:.1f} {x1:.1f},{y + r:.1f} "
        f"V{y + height - r:.1f} Q{x1:.1f},{y + height:.1f} {x1 - r:.1f},{y + height:.1f} "
        f"H{x0:.1f} Z"
    )


def speedup_chart(py: dict, rs: dict) -> str:
    """Horizontal bars: how many times faster Rust is than Python, per case."""
    names = ordered_names(py)
    speedups = {n: py[n] / rs[n] for n in names}
    width, left, right, top, row, bar = 760, 170, 60, 64, 26, 14
    plot_w = width - left - right
    height = top + row * len(names) + 40
    step = 5
    max_x = math.ceil(max(speedups.values()) / step) * step
    sx = plot_w / max_x

    out = svg_open(
        width, height, "Rust speedup over Python",
        "Python time divided by Rust time for each benchmark case. Higher means Rust is faster.",
    )
    out.append(f'<text class="t1" x="20" y="30" font-size="16" font-weight="600">'
               f"Rust speedup over Python</text>")
    out.append(f'<text class="t2" x="20" y="50" font-size="12">'
               f"Python time ÷ Rust time, median of 7 samples · higher = Rust faster</text>")
    axis_y = top + row * len(names)
    for v in range(0, max_x + 1, step):
        x = left + v * sx
        out.append(f'<line class="grid" x1="{x:.1f}" y1="{top - 6}" x2="{x:.1f}" y2="{axis_y}"/>')
        out.append(f'<text class="mut" x="{x:.1f}" y="{axis_y + 18}" font-size="11" '
                   f'text-anchor="middle">{v}×</text>')
    for i, name in enumerate(names):
        y = top + i * row + (row - bar) / 2
        s = speedups[name]
        out.append(f'<text class="t2" x="{left - 10}" y="{y + bar - 3}" font-size="12" '
                   f'text-anchor="end">{escape(label(name))}</text>')
        out.append(f'<path class="rs" d="{bar_path(left, y, s * sx, bar)}">'
                   f"<title>{escape(label(name))}: {s:.1f}× faster in Rust</title></path>")
        out.append(f'<text class="t1" x="{left + s * sx + 6:.1f}" y="{y + bar - 3}" '
                   f'font-size="12" font-weight="600">{s:.1f}×</text>')
    out.append("</svg>")
    return "\n".join(out)


def times_chart(py: dict, rs: dict) -> str:
    """Dumbbell chart on a log scale: Python and Rust time per operation."""
    names = ordered_names(py)
    width, left, right, top, row = 760, 170, 30, 84, 26
    plot_w = width - left - right
    height = top + row * len(names) + 40
    lo = 10 ** math.floor(math.log10(min(rs.values())))
    hi = 10 ** math.ceil(math.log10(max(py.values())))
    span = math.log10(hi) - math.log10(lo)

    def sx(ns: float) -> float:
        return left + (math.log10(ns) - math.log10(lo)) / span * plot_w

    out = svg_open(
        width, height, "Time per operation: Python vs Rust",
        "Median time per operation for each case on a logarithmic scale, "
        "Python in blue and Rust in orange. Lower is better.",
    )
    out.append(f'<text class="t1" x="20" y="30" font-size="16" font-weight="600">'
               f"Time per operation</text>")
    out.append(f'<text class="t2" x="20" y="50" font-size="12">'
               f"Median, log scale · lower is better · each step on the axis is 10×</text>")
    # Legend (two series): swatch + name, top left above the plot.
    out.append('<circle class="py" cx="26" cy="68" r="5"/>')
    out.append('<text class="t2" x="36" y="72" font-size="12">Python</text>')
    out.append('<circle class="rs" cx="96" cy="68" r="5"/>')
    out.append('<text class="t2" x="106" y="72" font-size="12">Rust</text>')

    axis_y = top + row * len(names)
    decade = lo
    while decade <= hi:
        x = sx(decade)
        out.append(f'<line class="grid" x1="{x:.1f}" y1="{top - 6}" x2="{x:.1f}" y2="{axis_y}"/>')
        out.append(f'<text class="mut" x="{x:.1f}" y="{axis_y + 18}" font-size="11" '
                   f'text-anchor="middle">{fmt_time(decade)}</text>')
        decade *= 10
    for i, name in enumerate(names):
        cy = top + i * row + row / 2
        xp, xr = sx(py[name]), sx(rs[name])
        out.append(f'<text class="t2" x="{left - 10}" y="{cy + 4}" font-size="12" '
                   f'text-anchor="end">{escape(label(name))}</text>')
        out.append(f'<line class="link" x1="{xr:.1f}" y1="{cy}" x2="{xp:.1f}" y2="{cy}"/>')
        for cls, x, ns, who in (("rs", xr, rs[name], "Rust"), ("py", xp, py[name], "Python")):
            out.append(f'<circle class="{cls} ring" cx="{x:.1f}" cy="{cy}" r="5">'
                       f"<title>{escape(label(name))} · {who}: {fmt_time(ns)}</title></circle>")
    out.append("</svg>")
    return "\n".join(out)
