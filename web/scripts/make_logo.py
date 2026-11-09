#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Maximilian Pierzyna
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""The logo and the favicon (public/): the climatology of the Cn2 profile as in the app's profile panel, without axes.
The 5-95 % and 25-75 % ranges and the median of log10 Cn2 at one grid cell, month and hour, over a logarithmic height
axis from the ground to `Z_MAX`, smoothed in log height. Blue on light (the app's climatology colour) for the light
theme, magma on dark for the dark one.

Writes logo-light.svg and logo-dark.svg (the header, per theme of the app), favicon.svg (both, switched by the
system's colour scheme: the browser tab does not know the app's theme) and favicon.png (light, for browsers without
SVG favicons). Run again only to change the design (the files are committed), from pipeline/:

    uv run --with matplotlib python ../web/scripts/make_logo.py [<web data dir>]
"""

import io
import json
import pathlib
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

HERE = pathlib.Path(__file__).resolve().parent
DATA = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "pipeline/data/webui"
PUBLIC = HERE.parent / "public"

LAT, LON, MONTH, HOUR = 52.0, 5.0, 11, 12  # grid cell, calendar month, hour [UTC] of the climatology
Z_MAX = 10_000.0  # m: the boundary layer takes the lower half of the log axis
SMOOTH = 0.08  # decades of height (Gaussian)
MARGIN = 0.11  # of the tile, around the plot
RADIUS = 0.18  # corner radius, of the tile
MEDIAN_WIDTH = 2.0  # pt; the tile is 72 pt

SCHEMES = {
    "light": {"bg": "#ffffff", "edge": "#d5dbe3", "outer": "#a9cdf3", "inner": "#2383e2", "median": "#0b2f57"},
    "dark": {"bg": "#1a0b2e", "edge": "#1a0b2e", "outer": "#8c2981", "inner": "#f1605d", "median": "#fde5a6"},
}


def load_bands() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """log10 height (even in log height up to `Z_MAX`) and the smoothed percentiles of log10 Cn2 there."""
    root = DATA / "climatology"
    meta = json.loads((root / "meta.json").read_text())
    v, z = meta["variables"]["lcn2"], np.array(meta["z_agl"])
    cell = meta["lat"].index(LAT) * len(meta["lon"]) + meta["lon"].index(LON)
    stats = v["diurnal_profiles"]["stats"]
    shape = (len(meta["months"]), len(meta["hours"]), len(stats), len(z))
    stored = np.fromfile(root / f"lcn2_diurnal/{cell}.bin", dtype="<u2").reshape(shape)
    profiles = stored[meta["months"].index(MONTH), meta["hours"].index(HOUR)]
    t = np.linspace(np.log10(z[0]), np.log10(Z_MAX), 100)
    # Linearly in log height onto the even grid first (the lowest heights are far apart in log height), then smoothed
    kernel = np.exp(-0.5 * ((t[:, None] - t[None, :]) / SMOOTH) ** 2)
    kernel /= kernel.sum(axis=1, keepdims=True)
    bands = {}
    for s in ("p5", "p25", "median", "p75", "p95"):
        values = v["offset"] + v["scale"] * profiles[stats.index(s)].astype(float)
        bands[s] = kernel @ np.interp(t, np.log10(z), values)
    return t, bands


def draw(t: np.ndarray, bands: dict[str, np.ndarray], colours: dict[str, str]) -> plt.Figure:
    """The tile, 1 inch (72 pt) square: rounded background, the two ranges, the median clipped to the outer range."""
    fig = plt.figure(figsize=(1, 1))
    fig.patch.set_alpha(0)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    inset = 0.5 / 72  # half the edge line: the tile stays within the image
    ax.add_patch(
        FancyBboxPatch(
            (inset, inset),
            1 - 2 * inset,
            1 - 2 * inset,
            boxstyle=f"round,pad=0,rounding_size={RADIUS}",
            facecolor=colours["bg"],
            edgecolor=colours["edge"],
            linewidth=1,
        )
    )
    lo, hi = bands["p5"].min(), bands["p95"].max()
    x = lambda v: MARGIN + (v - lo) / (hi - lo) * (1 - 2 * MARGIN)
    y = MARGIN + (t - t[0]) / (t[-1] - t[0]) * (1 - 2 * MARGIN)
    outer = ax.fill_betweenx(y, x(bands["p5"]), x(bands["p95"]), color=colours["outer"], linewidth=0)
    ax.fill_betweenx(y, x(bands["p25"]), x(bands["p75"]), color=colours["inner"], linewidth=0)
    (median,) = ax.plot(x(bands["median"]), y, color=colours["median"], linewidth=MEDIAN_WIDTH, solid_capstyle="butt")
    median.set_clip_path(outer.get_paths()[0], outer.get_transform())  # never beyond the climatology
    return fig


def save_svg(fig: plt.Figure, path: pathlib.Path, prefix: str) -> str:
    """`fig` as SVG at `path`, compact and reproducible: coordinates to 0.01 (of 72), no metadata (the matplotlib
    version), ids with `prefix` (both schemes share the favicon); returns the SVG."""
    plt.rcParams["svg.hashsalt"] = prefix
    buffer = io.StringIO()
    fig.savefig(buffer, format="svg", transparent=True, metadata={"Date": None})
    svg = re.sub(r"\s*<metadata>.*?</metadata>", "", buffer.getvalue(), flags=re.DOTALL)
    svg = re.sub(r"-?\d+\.\d{3,}", lambda m: f"{float(m.group()):.2f}".rstrip("0").rstrip("."), svg)
    svg = re.sub(r'(id="|url\(#|href="#)', rf"\1{prefix}-", svg)
    path.write_text(svg)
    return svg


def combine(svgs: dict[str, str]) -> str:
    """One SVG with both schemes, the dark one shown if the system's colour scheme is dark."""
    view_box = re.search(r'viewBox="([^"]+)"', svgs["light"]).group(1)
    inner = {k: re.search(r"<svg[^>]*>(.*)</svg>", s, re.DOTALL).group(1) for k, s in svgs.items()}
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{view_box}">\n'
        "<style>.dark{display:none}@media (prefers-color-scheme:dark){.light{display:none}.dark{display:inline}}</style>\n"
        f'<g class="light">{inner["light"]}</g>\n<g class="dark">{inner["dark"]}</g>\n</svg>\n'
    )


if __name__ == "__main__":
    t, bands = load_bands()
    svgs = {}
    for name, colours in SCHEMES.items():
        fig = draw(t, bands, colours)
        svgs[name] = save_svg(fig, PUBLIC / f"logo-{name}.svg", prefix=name)
        if name == "light":
            fig.savefig(PUBLIC / "favicon.png", dpi=64, transparent=True)  # 64 px
        plt.close(fig)
    (PUBLIC / "favicon.svg").write_text(combine(svgs))
    for f in ("logo-light.svg", "logo-dark.svg", "favicon.svg", "favicon.png"):
        print(f, (PUBLIC / f).stat().st_size, "bytes")
