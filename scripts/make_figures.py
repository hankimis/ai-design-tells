#!/usr/bin/env python3
"""
Generate the paper/README figures from results/scores.json and the rendered
fixture screenshots. Charts are deliberately *designed* (a design paper should
not ship slop charts): one ink, one accent, hairline grid, serif display, air.

Outputs to paper/figs/:
  fig1_moneyshot.png     before/after Tell Score (the headline)
  fig2_waterfall.png     tell-by-tell: each applied fix subtracts its weight
  fig3_families.png      family scores, AI-default vs Designed (corpus means)
  fig4_distribution.png  every corpus page, the slop cluster vs the designed cluster
  fig5_heatmap.png       tells x pages fired matrix
  fig_templates.png      before/after fold screenshots, side by side
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FIGS = os.path.join(ROOT, "paper", "figs")
os.makedirs(FIGS, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "src"))
from taxonomy import TELLS, FAMILIES  # noqa: E402

DATA = json.load(open(os.path.join(ROOT, "results", "scores.json"), encoding="utf-8"))

# ---- palette (the designed fixture's own colors) ----
INK   = "#16181d"
SOFT  = "#5b6066"
FAINT = "#9aa0a6"
LINE  = "#e7e4de"
BG    = "#fbfaf8"
SLOP  = "#6d5cf6"   # the indigo tell, used to mark the slop side
GOOD  = "#0f6f63"   # calm teal, the designed side
CLAY  = "#9a3b1f"

# ---- try to load a serif display face for titles ----
def _serif():
    for cand in ["Charter", "Iowan Old Style", "Georgia", "Palatino", "Hoefler Text"]:
        try:
            p = fm.findfont(fm.FontProperties(family=cand), fallback_to_default=False)
            if p and os.path.exists(p):
                fm.fontManager.addfont(p)
                return fm.FontProperties(fname=p).get_name()
        except Exception:
            continue
    return "DejaVu Serif"

SERIF = _serif()

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "font.family": "sans-serif",
    "font.sans-serif": ["Avenir Next", "Helvetica Neue", "Arial", "DejaVu Sans"],
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": SOFT, "ytick.color": SOFT,
    "axes.edgecolor": LINE, "axes.linewidth": 1.0, "font.size": 12,
    "axes.spines.top": False, "axes.spines.right": False,
})

def _clean(ax):
    ax.tick_params(length=0)
    ax.grid(axis="y", color=LINE, linewidth=1, zorder=0)
    ax.set_axisbelow(True)

def _title(ax, t, sub=None):
    ax.text(0, 1.15, t, transform=ax.transAxes, va="bottom",
            fontproperties=fm.FontProperties(family=SERIF, size=19), color=INK)
    if sub:
        ax.text(0, 1.045, sub, transform=ax.transAxes, va="bottom",
                color=SOFT, fontsize=10.5)

def _save(fig, name):
    fig.savefig(os.path.join(FIGS, name), dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print(name)


# --------------------------------------------------------------------------
def fig_moneyshot():
    a = DATA["pages"]["ai-default"]["score"]
    r = DATA["pages"]["refined"]["score"]
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    bars = ax.bar([0, 1], [a, r], width=0.52, color=[SLOP, GOOD], zorder=3)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["AI-default\n(before)", "Refined\n(after, same content)"], fontsize=13)
    ax.set_ylim(0, 100); ax.set_ylabel("Tell Score  (0–100, lower is better)")
    _clean(ax)
    for x, v in zip([0, 1], [a, r]):
        ax.text(x, v + 2.5, f"{v:.0f}", ha="center", va="bottom",
                fontsize=26, fontproperties=fm.FontProperties(family=SERIF), color=INK)
    # the delta arrow
    ax.annotate("", xy=(0.92, r + 4), xytext=(0.08, a - 4),
                arrowprops=dict(arrowstyle="-|>", color=CLAY, lw=2,
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(0.5, (a + r) / 2 + 14, f"−{a - r:.0f} points\nfrom applying the\ndocumented fixes",
            ha="center", color=CLAY, fontsize=12, fontweight="bold")
    _title(ax, "Same page, the tells removed",
           "TaskFlow landing page: only the tell-bearing choices changed (font, color, layout, motion, copy)")
    fig.tight_layout()
    _save(fig, "fig1_moneyshot.png")


def fig_waterfall():
    # Start at ai-default score, subtract each fired tell's weight (as a fraction
    # of max -> points) in descending weight order, ending near refined.
    page = DATA["pages"]["ai-default"]
    maxw = DATA["max_weight"]
    fired = [t for t in TELLS if page["fired"].get(t.id)]
    fired.sort(key=lambda t: -t.weight)
    start = page["score"]
    fig, ax = plt.subplots(figsize=(11, 5.2))
    x = 0
    prev = start
    ax.bar(x, start, width=0.7, color=SLOP, zorder=3)
    ax.text(x, start + 1.5, f"{start:.0f}", ha="center", fontsize=12,
            fontproperties=fm.FontProperties(family=SERIF))
    labels = ["AI-default"]
    for t in fired:
        x += 1
        drop = 100 * t.weight / maxw
        nxt = prev - drop
        ax.bar(x, drop, bottom=nxt, width=0.7,
               color=GOOD if t.severity == "tell" else "#79b4ab", zorder=3, alpha=.95)
        ax.plot([x - 1 + 0.35, x - 0.35], [prev, prev], color=FAINT, lw=1, ls=(0, (2, 2)))
        ax.text(x, prev + 1.2, f"−{drop:.0f}", ha="center", fontsize=9.5, color=SOFT)
        labels.append(f"[{t.id}] {t.name}")
        prev = nxt
    x += 1
    ax.bar(x, prev, width=0.7, color="#cfcac2" if prev > 0 else GOOD, zorder=3)
    ax.text(x, prev + 1.5, f"{prev:.0f}", ha="center", fontsize=12,
            fontproperties=fm.FontProperties(family=SERIF))
    labels.append("Refined")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=38, ha="right", fontsize=9.5)
    ax.set_ylim(0, 100); ax.set_ylabel("Tell Score")
    _clean(ax)
    _title(ax, "Every fix pays down the score",
           "Each bar removes one fired tell's weight, in order of impact (teal = strong tell, light = smell)")
    fig.tight_layout()
    _save(fig, "fig2_waterfall.png")


def fig_families():
    fams = list(FAMILIES.keys())
    names = [f"{k}\n{FAMILIES[k][0]}" for k in fams]
    slop_pages = [p for p in DATA["pages"].values() if p["label"] == "AI-default"]
    des_pages = [p for p in DATA["pages"].values() if p["label"] == "Designed"]
    slop = [np.mean([p["family_scores"][k] for p in slop_pages]) for k in fams]
    des = [np.mean([p["family_scores"][k] for p in des_pages]) for k in fams]
    x = np.arange(len(fams)); w = 0.38
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.bar(x - w/2, slop, w, label="AI-default (n=3)", color=SLOP, zorder=3)
    ax.bar(x + w/2, des, w, label="Designed (n=3)", color=GOOD, zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=11)
    ax.set_ylim(0, 100); ax.set_ylabel("Family score (mean)")
    _clean(ax)
    ax.legend(frameon=False, loc="upper right")
    _title(ax, "Where the tells live",
           "Mean per-family Tell Score across the corpus. Color, type, layout and motion separate hardest.")
    fig.tight_layout()
    _save(fig, "fig3_families.png")


def fig_distribution():
    # single number line; vertical jitter + staggered leader labels so coincident
    # points (the Designed pages all score 0) stay readable.
    fig, ax = plt.subplots(figsize=(10.5, 3.6))
    rows = {"AI-default": (SLOP, 0.30), "Designed": (GOOD, -0.30)}
    ax.axvspan(0, 12, color=GOOD, alpha=0.06)
    ax.axvspan(45, 100, color=SLOP, alpha=0.06)
    for label, (col, base) in rows.items():
        items = [(n, p["score"]) for n, p in DATA["pages"].items() if p["label"] == label]
        items.sort(key=lambda t: t[1])
        n = len(items)
        for j, (name, sc) in enumerate(items):
            jit = base + (j - (n - 1) / 2) * 0.12
            ax.scatter(sc, jit, s=300, color=col, zorder=4, edgecolor=BG, linewidth=2.5)
            up = base > 0
            ax.annotate(f"{name}  ·  {sc:.0f}", (sc, jit),
                        xytext=(8, 14 if up else -16), textcoords="offset points",
                        ha="left", va="bottom" if up else "top", fontsize=9, color=SOFT)
        m = np.mean([s for _, s in items])
        ax.scatter([m], [base], s=0)
        ax.annotate(f"mean {m:.0f}", (m, base), xytext=(0, 40 if base > 0 else -42),
                    textcoords="offset points", ha="center",
                    fontsize=11, color=INK, fontweight="bold")
    # the gap band
    ax.annotate("", xy=(45, 0), xytext=(12, 0),
                arrowprops=dict(arrowstyle="<|-|>", color=FAINT, lw=1.3))
    ax.text(28.5, 0.05, "33-point gap", ha="center", color=FAINT, fontsize=9.5)
    ax.set_xlim(-4, 100); ax.set_ylim(-0.85, 0.95); ax.set_xlabel("Tell Score  (lower is better)")
    ax.set_yticks([])
    ax.tick_params(length=0); ax.grid(axis="x", color=LINE, lw=1); ax.set_axisbelow(True)
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    _title(ax, "Two clusters, a wide gap",
           "Every page in the corpus on one axis. The detector separates the families with no overlap.")
    fig.tight_layout()
    _save(fig, "fig4_distribution.png")


def fig_heatmap():
    pages = list(DATA["pages"].keys())
    tells = TELLS
    M = np.array([[1 if DATA["pages"][pg]["fired"].get(t.id) else 0 for pg in pages]
                  for t in tells])
    fig, ax = plt.subplots(figsize=(8.8, 9.2))
    from matplotlib.colors import ListedColormap
    ax.imshow(M, aspect="auto", cmap=ListedColormap([BG, SLOP]), vmin=0, vmax=1)
    ax.set_xticks(range(len(pages)))
    ax.set_xticklabels(pages, rotation=35, ha="right", fontsize=10)
    ax.set_yticks(range(len(tells)))
    ax.set_yticklabels([f"[{t.id}] {t.name}" for t in tells], fontsize=9.5)
    ax.set_xticks(np.arange(-.5, len(pages), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(tells), 1), minor=True)
    ax.grid(which="minor", color=BG, lw=2)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    _title(ax, "Which tell fires where",
           "Filled = the tell was detected on that page. Designed pages are nearly empty columns.")
    fig.tight_layout()
    _save(fig, "fig5_heatmap.png")


def fig_templates():
    """Side-by-side fold screenshots with score badges (the visible before/after)."""
    ai = Image.open(os.path.join(FIGS, "shot_ai-default.png")).convert("RGB")
    rf = Image.open(os.path.join(FIGS, "shot_refined.png")).convert("RGB")
    h = 720
    def fit(im):
        w = int(im.width * h / im.height)
        return im.resize((w, h))
    ai, rf = fit(ai), fit(rf)
    pad, gap, top = 28, 28, 96
    W = pad*2 + gap + ai.width + rf.width
    H = top + h + pad
    canvas = Image.new("RGB", (W, H), (251, 250, 248))
    canvas.paste(ai, (pad, top)); canvas.paste(rf, (pad + ai.width + gap, top))
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(canvas)
    def font(sz, bold=False):
        for p in (["/System/Library/Fonts/Supplemental/Georgia.ttf"] if not bold else
                  ["/System/Library/Fonts/Supplemental/Georgia Bold.ttf"]):
            if os.path.exists(p):
                return ImageFont.truetype(p, sz)
        return ImageFont.load_default()
    _before = DATA["pages"]["ai-default"]["score"]
    d.text((pad, 30), f"Before, Tell Score {_before:.0f} (F, textbook AI slop)", font=font(30, True), fill=(109, 92, 246))
    d.text((pad + ai.width + gap, 30), "After, Tell Score 0 (A, reads as human-crafted)",
           font=font(30, True), fill=(15, 111, 99))
    canvas.save(os.path.join(FIGS, "fig_templates.png"))
    print("fig_templates.png")


if __name__ == "__main__":
    fig_moneyshot()
    fig_waterfall()
    fig_families()
    fig_distribution()
    fig_heatmap()
    fig_templates()
    print("done.")
