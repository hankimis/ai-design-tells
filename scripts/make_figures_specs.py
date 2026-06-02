#!/usr/bin/env python3
"""
Figures for the component-spec catalog (data/spec_catalog.json).

  fig10_specsheet.png   four panels: button radii, the real type scale, dark-mode
                        backgrounds (actual near-black hexes), light accent diversity
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FIGS = os.path.join(ROOT, "paper", "figs")
os.makedirs(FIGS, exist_ok=True)
CAT = json.load(open(os.path.join(ROOT, "data", "spec_catalog.json")))

INK = "#16181d"; SOFT = "#5b6066"; FAINT = "#9aa0a6"; LINE = "#e7e4de"; BG = "#fbfaf8"
ACC = "#0f6f63"; SLOP = "#6d5cf6"


def _sans():
    for c in ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"]:
        try:
            fm.findfont(c, fallback_to_default=False); return c
        except Exception:
            pass
    return "DejaVu Sans"


plt.rcParams.update({"font.family": _sans(), "axes.edgecolor": LINE,
                     "text.color": INK, "axes.labelcolor": INK,
                     "xtick.color": SOFT, "ytick.color": SOFT})


def panel_button_radius(ax):
    pr = CAT["buttons"].get("primary", {})
    common = pr.get("radius_px", {}).get("common", [])
    if not common:
        ax.axis("off"); return
    vals = [str(int(v)) for v, _ in common]
    counts = [c for _, c in common]
    ax.bar(vals, counts, color=ACC, width=0.66)
    med = pr["radius_px"]["median"]
    ax.set_title(f"Primary button radius (median {med}px)", fontsize=11, loc="left", color=INK, pad=8)
    ax.set_xlabel("border-radius (px)", fontsize=9)
    ax.set_ylabel("sites", fontsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def panel_type_scale(ax):
    tags = ["h1", "h2", "h3", "body"]
    sizes, labels = [], []
    for t in tags:
        v = CAT["typography"].get(t, {}).get("font_size_px", {}).get("median")
        if v:
            sizes.append(v); labels.append(t)
    y = np.arange(len(labels))[::-1]
    ax.barh(y, sizes, color=INK, height=0.6)
    for yi, s, lab in zip(y, sizes, labels):
        ax.text(s + 1.5, yi, f"{s:g}px", va="center", fontsize=9, color=SOFT)
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=10)
    ax.set_title("The real type scale (median size)", fontsize=11, loc="left", color=INK, pad=8)
    ax.set_xlabel("font-size (px)", fontsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def _swatches(ax, pairs, title, text_on_dark=False):
    ax.set_title(title, fontsize=11, loc="left", color=INK, pad=8)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    n = min(len(pairs), 8)
    if not n:
        return
    w = 10.0 / n
    for i, (hexv, cnt) in enumerate(pairs[:n]):
        try:
            ax.add_patch(plt.Rectangle((i * w + 0.1, 2.2), w - 0.2, 6.2,
                                       facecolor=hexv, edgecolor=LINE, linewidth=0.8))
        except Exception:
            continue
        tcol = "#ffffff" if text_on_dark else INK
        ax.text(i * w + w / 2, 1.4, hexv, ha="center", va="top", fontsize=7.0,
                color=SOFT, rotation=0)
        ax.text(i * w + w / 2, 5.3, str(cnt), ha="center", va="center", fontsize=9,
                color=tcol, weight="bold")


def fig_sample():
    """Side-by-side light/dark of the built-to-catalog sample (fixtures/catalog-sample.html)."""
    from PIL import Image, ImageDraw, ImageFont
    L = Image.open(os.path.join(FIGS, "sample_light.png")).convert("RGB")
    D = Image.open(os.path.join(FIGS, "sample_dark.png")).convert("RGB")
    h = 760
    fit = lambda im: im.resize((int(im.width * h / im.height), h))
    L, D = fit(L), fit(D)
    pad, gap, top = 26, 26, 92
    W = pad * 2 + gap + L.width + D.width
    H = top + h + pad
    canvas = Image.new("RGB", (W, H), (251, 250, 248))
    canvas.paste(L, (pad, top)); canvas.paste(D, (pad + L.width + gap, top))
    d = ImageDraw.Draw(canvas)

    def font(sz, bold=False):
        for p in (["/System/Library/Fonts/Supplemental/Georgia Bold.ttf"] if bold else
                  ["/System/Library/Fonts/Supplemental/Georgia.ttf"]):
            if os.path.exists(p):
                return ImageFont.truetype(p, sz)
        return ImageFont.load_default()

    d.text((pad, 26), "Built to the catalog, light", font=font(28, True), fill=(26, 28, 30))
    d.text((pad, 58), "Tell Score 0  ·  1200px grid, 64/48/32px type, 8px buttons", font=font(17), fill=(91, 96, 102))
    d.text((pad + L.width + gap, 26), "Same page, dark", font=font(28, True), fill=(184, 70, 15))
    d.text((pad + L.width + gap, 58), "tinted near-black #0e1014, surfaces a step lighter, off-white text",
           font=font(17), fill=(91, 96, 102))
    out = os.path.join(FIGS, "fig11_sample.png")
    canvas.save(out)
    print("wrote", out)


def main():
    fig_sample()
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    fig.patch.set_facecolor(BG)
    for ax in axes.flat:
        ax.set_facecolor(BG)
    panel_button_radius(axes[0, 0])
    panel_type_scale(axes[0, 1])
    _swatches(axes[1, 0], CAT["color"]["dark"]["page_bg_common"],
              f"Dark-mode page backgrounds ({CAT['color']['n_dark_mode']}/{CAT['color']['n_total']} sites)",
              text_on_dark=True)
    _swatches(axes[1, 1], CAT["color"]["light"]["accent_common"],
              "Accent colors: no single 'correct' hue")
    fig.suptitle("What real top-tier sites ship, by component",
                 fontsize=14, x=0.07, ha="left", y=0.98, color=INK, weight="bold")
    fig.text(0.07, 0.945, f"measured across {CAT['n_sites']} human-crafted, design-led sites",
             fontsize=10, color=SOFT, ha="left")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    out = os.path.join(FIGS, "fig10_specsheet.png")
    fig.savefig(out, dpi=170, facecolor=BG, bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main()
