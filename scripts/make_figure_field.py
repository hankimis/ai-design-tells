#!/usr/bin/env python3
"""
fig13_field.png  ·  the field-evidence figure (v4).

Two production codebases with owner-authored "avoid the AI look" design
manifestos independently named six tells the v1-v3 taxonomy did not cover. This
figure shows those six (the new family H plus A4/B4/E4), their weights, and which
of the two anonymized manifestos named each. It is the bridge from "we enumerated
the look" to "working practitioners enumerated the same look, and more."
"""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FIGS = os.path.join(ROOT, "paper", "figs")
sys.path.insert(0, os.path.join(ROOT, "src"))
from taxonomy import TELLS  # noqa: E402

INK = "#16181d"; SOFT = "#5b6066"; FAINT = "#9aa0a6"; LINE = "#e7e4de"; BG = "#fbfaf8"
HFAM = "#9a3b1f"   # clay, marks the new family H
OTHER = "#0f6f63"  # teal, the additions to existing families
DOT = "#16181d"

def _serif():
    for cand in ["Charter", "Iowan Old Style", "Georgia", "Palatino"]:
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
    "axes.edgecolor": LINE, "font.size": 12,
})

WT = {t.id: t.weight for t in TELLS}
NAME = {t.id: t.name for t in TELLS}

# rows top-to-bottom; (id, named-by-A, named-by-B), A = dark-mode media tool,
# B = productivity assistant. Honest attribution from the two manifestos.
ROWS = [
    ("H1", False, True),
    ("H2", False, True),
    ("H3", False, True),
    ("E4", False, True),
    ("A4", True,  True),
    ("B4", True,  True),
]

fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.6, 5.0),
                               gridspec_kw={"width_ratios": [2.5, 1.0]})

# ---- left: weight bars ----
ids = [r[0] for r in ROWS][::-1]
ys = range(len(ids))
for y, tid in zip(ys, ids):
    col = HFAM if tid.startswith("H") else OTHER
    axL.barh(y, WT[tid], height=0.6, color=col, zorder=3)
    axL.text(WT[tid] + 0.12, y, f"{WT[tid]:.0f}", va="center", fontsize=11, color=SOFT)
    axL.text(-0.2, y, f"[{tid}] {NAME[tid]}", va="center", ha="right", fontsize=11.5, color=INK)
axL.set_xlim(0, 6.4); axL.set_ylim(-0.6, len(ids) - 0.4)
axL.set_yticks([]); axL.set_xlabel("weight in the Tell Score")
axL.tick_params(length=0); axL.grid(axis="x", color=LINE, lw=1); axL.set_axisbelow(True)
for s in ("left", "right", "top"):
    axL.spines[s].set_visible(False)
axL.text(0, 1.17, "Six tells the field named, the taxonomy missed", transform=axL.transAxes,
         fontproperties=fm.FontProperties(family=SERIF, size=19), color=INK)
axL.text(0, 1.07, "Clay = the new family H (AI self-reference); teal = additions to existing families.",
         transform=axL.transAxes, color=SOFT, fontsize=10.5)

# ---- right: coverage matrix ----
cols = ["Manifesto A\n(media tool)", "Manifesto B\n(assistant)"]
axR.set_xlim(-0.5, 1.5); axR.set_ylim(-0.6, len(ids) + 1.0)
for j, c in enumerate(cols):
    axR.text(j, len(ids) - 0.35, c, ha="center", va="bottom", fontsize=9.5, color=INK)
for y, (tid, a, b) in zip(ys, ROWS[::-1]):
    for j, named in enumerate((a, b)):
        if named:
            axR.scatter(j, y, s=130, color=DOT, zorder=3)
        else:
            axR.scatter(j, y, s=130, facecolors="none", edgecolors=FAINT, linewidth=1.2, zorder=3)
axR.set_xticks([]); axR.set_yticks([])
for s in axR.spines.values():
    s.set_visible(False)
axR.text(0.5, 1.17, "Named by", transform=axR.transAxes, ha="center",
         fontproperties=fm.FontProperties(family=SERIF, size=15), color=INK)

fig.text(0.5, 0.005, "Two production codebases, owner-authored manifestos. Filled dot = that manifesto explicitly bans the pattern.",
         ha="center", color=SOFT, fontsize=9.5)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(os.path.join(FIGS, "fig13_field.png"), dpi=200, bbox_inches="tight", pad_inches=0.3)
print("fig13_field.png")
