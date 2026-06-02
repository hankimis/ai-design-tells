#!/usr/bin/env python3
"""
Render fixtures/catalog-sample.html to light + dark screenshots, the same page the
v3 catalog describes, shown in both palettes. Writes:
  paper/figs/sample_light.png   the built-to-catalog sample, light
  paper/figs/sample_dark.png    same page, prefers-color-scheme: dark
Plus a tall full-fold capture of each for the gallery.
"""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FIG = os.path.join(ROOT, "paper", "figs")
URL = "file://" + os.path.join(ROOT, "fixtures", "catalog-sample.html")
os.makedirs(FIG, exist_ok=True)


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        for scheme in ("light", "dark"):
            ctx = b.new_context(viewport={"width": 1440, "height": 1024},
                                device_scale_factor=2, color_scheme=scheme)
            pg = ctx.new_page()
            pg.goto(URL, wait_until="networkidle")
            pg.wait_for_timeout(500)
            # above-the-fold money shot (hero + proof + top of bento)
            pg.screenshot(path=os.path.join(FIG, f"sample_{scheme}.png"),
                          clip={"x": 0, "y": 0, "width": 1440, "height": 980})
            # full page for the gallery
            pg.screenshot(path=os.path.join(FIG, f"sample_{scheme}_full.png"), full_page=True)
            print(f"rendered sample_{scheme}.png + full")
            ctx.close()
        b.close()


if __name__ == "__main__":
    main()
