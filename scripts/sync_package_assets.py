#!/usr/bin/env python3
"""
Sync the distilled data + harness into the package directory so a built wheel
bundles current copies.

The canonical generators (build_spec_catalog.py, build_korean_catalog.py,
analyze_corpus.py, gen_harness.py) write to the repo's `data/` and `harness/`.
In a dev checkout the package reads those directly; but an installed wheel cannot
see the repo, so it ships its own copy under `ai_design_tells/`. This script
refreshes that copy. The release workflow runs it before `python -m build`.
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "ai_design_tells")

ASSETS = [
    "data/spec_catalog.json",
    "data/korean_catalog.json",
    "data/calibration.json",
    "harness/AI-DESIGN-TELLS.md",
]


def main():
    for rel in ASSETS:
        src = os.path.join(ROOT, rel)
        dst = os.path.join(PKG, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        print(f"synced {rel} -> ai_design_tells/{rel}")


if __name__ == "__main__":
    main()
