#!/usr/bin/env python3
"""
gif_lightdark.gif, the built-to-catalog sample crossfading between light and dark.
The point of the v3 catalog made visible: same page, two palettes, and the dark
one follows the measured grammar (a tinted near-black, surfaces a step lighter,
an off-white text, the accent warmed) rather than inverting to pure black.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "..", "paper", "figs")

LIGHT_BG = (251, 250, 248); LIGHT_INK = (26, 28, 30)
DARK_BG = (14, 16, 20); DARK_INK = (231, 232, 234)
ACCENT = (184, 70, 15)


def _font(sz, bold=False):
    for p in [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf" if bold else
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def _lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def main():
    a = Image.open(os.path.join(FIGS, "sample_light.png")).convert("RGB")
    b = Image.open(os.path.join(FIGS, "sample_dark.png")).convert("RGB")
    w = 860
    fit = lambda im: im.resize((w, int(im.height * w / im.width)))
    a, b = fit(a), fit(b)
    h = min(a.height, b.height)
    a, b = a.crop((0, 0, w, h)), b.crop((0, 0, w, h))
    cap_h = 60
    H = h + cap_h
    frames, durs = [], []

    def compose(img, t):
        bg = _lerp(LIGHT_BG, DARK_BG, t)
        ink = _lerp(LIGHT_INK, DARK_INK, t)
        c = Image.new("RGB", (w, H), bg)
        c.paste(img, (0, cap_h))
        d = ImageDraw.Draw(c)
        label = "Same page, light" if t < 0.5 else "Same page, dark: a tinted near-black"
        d.text((24, 17), label, font=_font(24, True), fill=ink)
        # a small swatch showing the page bg actually in use
        sw = _lerp(LIGHT_BG, DARK_BG, t)
        d.rounded_rectangle([w - 150, 20, w - 24, cap_h - 16], radius=8,
                            fill=sw, outline=_lerp((220, 218, 212), (60, 64, 70), t), width=1)
        bgs = "#ffffff" if t < 0.5 else "#0e1014"
        d.text((w - 142, 27), f"page  {bgs}", font=_font(13), fill=ink)
        return c

    # hold light
    for _ in range(11):
        frames.append(compose(a, 0.0)); durs.append(80)
    # fade to dark
    N = 16
    for i in range(N + 1):
        t = i / N
        frames.append(compose(Image.blend(a, b, t), t)); durs.append(70)
    # hold dark
    for _ in range(14):
        frames.append(compose(b, 1.0)); durs.append(80)
    # fade back
    for i in range(N + 1):
        t = 1 - i / N
        frames.append(compose(Image.blend(a, b, t), t)); durs.append(70)

    pal = frames[len(frames) // 2].quantize(colors=128, method=Image.FASTOCTREE)
    q = [f.quantize(colors=128, palette=pal, dither=Image.Dither.NONE) for f in frames]
    out = os.path.join(FIGS, "gif_lightdark.gif")
    q[0].save(out, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True)
    sz = os.path.getsize(out) // 1024
    print(f"gif_lightdark.gif ({len(frames)} frames, {sz} KB)")


if __name__ == "__main__":
    main()
