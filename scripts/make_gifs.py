#!/usr/bin/env python3
"""
Animated figures:
  gif_reveal.gif     before->after crossfade of the two template folds, with a
                     score badge counting 76 -> 0 (the money-shot animation)
  gif_waterfall.gif  the waterfall building one fix at a time
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FIGS = os.path.join(ROOT, "paper", "figs")
sys.path.insert(0, os.path.join(ROOT, "src"))
from taxonomy import TELLS  # noqa: E402
DATA = json.load(open(os.path.join(ROOT, "results", "scores.json"), encoding="utf-8"))

BG = (251, 250, 248); INK = (22, 24, 29); SLOP = (109, 92, 246); GOOD = (15, 111, 99)


def _font(sz, bold=False):
    for p in ([
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf" if bold else
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def _lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _badge(frame, score, col, grade):
    d = ImageDraw.Draw(frame)
    W = frame.width
    bw, bh = 250, 96
    x, y = W - bw - 28, 24
    d.rounded_rectangle([x, y, x + bw, y + bh], radius=18, fill=col)
    d.text((x + 22, y + 16), f"{score:.0f}", font=_font(54, True), fill=(255, 255, 255))
    d.text((x + 118, y + 22), "Tell Score", font=_font(18), fill=(255, 255, 255))
    d.text((x + 118, y + 50), grade, font=_font(20, True), fill=(255, 255, 255))


def reveal():
    before = DATA["pages"]["ai-default"]["score"]
    a = Image.open(os.path.join(FIGS, "shot_ai-default.png")).convert("RGB")
    b = Image.open(os.path.join(FIGS, "shot_refined.png")).convert("RGB")
    w = 820
    def fit(im):
        return im.resize((w, int(im.height * w / im.width)))
    a, b = fit(a), fit(b)
    h = min(a.height, b.height)
    a, b = a.crop((0, 0, w, h)), b.crop((0, 0, w, h))
    cap_h = 64
    canvas_h = h + cap_h
    frames, durs = [], []

    def compose(img, score, col, grade, caption):
        c = Image.new("RGB", (w, canvas_h), BG)
        c.paste(img, (0, cap_h))
        _badge(c, score, col, grade)
        d = ImageDraw.Draw(c)
        d.text((24, 18), caption, font=_font(28, True), fill=INK)
        return c

    # hold before
    for _ in range(9):
        frames.append(compose(a, before, SLOP, "F  ·  AI slop", "Before: the AI default"))
        durs.append(80)
    # crossfade with counting score
    N = 16
    for i in range(N + 1):
        t = i / N
        blend = Image.blend(a, b, t)
        score = before * (1 - t)
        col = _lerp(SLOP, GOOD, t)
        grade = "F  ·  AI slop" if t < 0.5 else "A  ·  human-crafted"
        frames.append(compose(blend, score, col, grade, "Removing the tells…"))
        durs.append(70)
    # hold after
    for _ in range(13):
        frames.append(compose(b, 0, GOOD, "A  ·  human-crafted", "After: same content, designed"))
        durs.append(80)
    # quantize to a shared palette to keep the GIF small
    pal = frames[len(frames)//2].quantize(colors=96, method=Image.FASTOCTREE)
    qframes = [f.quantize(colors=96, palette=pal, dither=Image.Dither.NONE) for f in frames]
    qframes[0].save(os.path.join(FIGS, "gif_reveal.gif"), save_all=True,
                    append_images=qframes[1:], duration=durs, loop=0, optimize=True)
    print("gif_reveal.gif", f"({len(frames)} frames)")


def waterfall():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm
    LINE = "#e7e4de"; SOFT = "#5b6066"; FAINT = "#9aa0a6"
    page = DATA["pages"]["ai-default"]; maxw = DATA["max_weight"]
    fired = [t for t in TELLS if page["fired"].get(t.id)]
    fired.sort(key=lambda t: -t.weight)
    start = page["score"]
    serif = "DejaVu Serif"
    for cand in ["Georgia", "Charter", "Palatino"]:
        try:
            p = fm.findfont(fm.FontProperties(family=cand), fallback_to_default=False)
            if p and os.path.exists(p):
                fm.fontManager.addfont(p); serif = fm.FontProperties(fname=p).get_name(); break
        except Exception:
            pass
    labels = ["AI-default"] + [f"[{t.id}] {t.name}" for t in fired] + ["Refined"]
    drops = [100 * t.weight / maxw for t in fired]
    levels = [start]
    for dz in drops:
        levels.append(levels[-1] - dz)
    frames = []
    tmp = os.path.join(ROOT, "results", "_wf")
    os.makedirs(tmp, exist_ok=True)
    for k in range(len(fired) + 2):  # reveal step by step
        fig, ax = plt.subplots(figsize=(11, 5.4))
        fig.patch.set_facecolor("#fbfaf8"); ax.set_facecolor("#fbfaf8")
        ax.bar(0, start, width=0.7, color="#6d5cf6", zorder=3)
        ax.text(0, start + 1.5, f"{start:.0f}", ha="center", fontsize=12,
                fontproperties=fm.FontProperties(family=serif))
        prev = start
        for j, t in enumerate(fired):
            if j + 1 > k:
                break
            dz = drops[j]; nxt = prev - dz
            ax.bar(j + 1, dz, bottom=nxt, width=0.7,
                   color="#0f6f63" if t.severity == "tell" else "#79b4ab", zorder=3)
            ax.plot([j + 0.35, j + 1 - 0.35], [prev, prev], color=FAINT, lw=1, ls=(0, (2, 2)))
            ax.text(j + 1, prev + 1.2, f"-{dz:.0f}", ha="center", fontsize=9, color=SOFT)
            prev = nxt
        if k >= len(fired) + 1:
            ax.bar(len(fired) + 1, prev, width=0.7, color="#0f6f63", zorder=3)
            ax.text(len(fired) + 1, prev + 1.5, f"{prev:.0f}", ha="center", fontsize=12,
                    fontproperties=fm.FontProperties(family=serif))
        ax.set_xlim(-0.7, len(labels) - 0.3); ax.set_ylim(0, 100)
        ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, rotation=38, ha="right", fontsize=9)
        ax.set_ylabel("Tell Score"); ax.tick_params(length=0)
        ax.grid(axis="y", color=LINE, lw=1); ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.text(0, 1.12, "Every fix pays down the score", transform=ax.transAxes,
                fontproperties=fm.FontProperties(family=serif, size=19), color="#16181d")
        fig.tight_layout()
        fp = os.path.join(tmp, f"wf_{k:02d}.png")
        fig.savefig(fp, dpi=150, bbox_inches="tight", pad_inches=0.25, facecolor="#fbfaf8")
        plt.close(fig)
        frames.append(Image.open(fp).convert("RGB"))
    # normalize sizes
    w0, h0 = frames[-1].size
    frames = [f.resize((w0, h0)) for f in frames]
    durs = [90] * len(frames)
    durs[0] = 700; durs[-1] = 1600
    frames[0].save(os.path.join(FIGS, "gif_waterfall.gif"), save_all=True,
                   append_images=frames[1:], duration=durs, loop=0, optimize=True)
    print("gif_waterfall.gif", f"({len(frames)} frames)")


if __name__ == "__main__":
    reveal()
    waterfall()
    print("done.")
