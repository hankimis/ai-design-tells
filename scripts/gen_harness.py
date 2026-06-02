#!/usr/bin/env python3
"""
Generate the drop-in MD harness (harness/AI-DESIGN-TELLS.md) from the taxonomy,
so the prevention guidance can never drift from what the detector measures.

The harness is meant to be pasted into a coding agent's system prompt / CLAUDE.md
/ .cursorrules. It turns each *detected* tell into a *preventive* instruction.
"""
import os, sys, json, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from taxonomy import TELLS, FAMILIES, tells_by_family  # noqa: E402

OUT = os.path.join(ROOT, "harness", "AI-DESIGN-TELLS.md")
CATALOG = os.path.join(ROOT, "data", "spec_catalog.json")


def spec_block():
    """Concrete target values measured from N real sites (data/spec_catalog.json).
    Kept in the harness so a builder gets numbers, not just don'ts. Regenerated
    from the catalog so it never drifts."""
    if not os.path.exists(CATALOG):
        return ""
    c = json.load(open(CATALOG))
    n = c["n_sites"]
    bp = c["buttons"].get("primary", {})
    h1 = c["typography"].get("h1", {}); body = c["typography"].get("body", {})
    lay = c["layout"]; col = c["color"]
    fmt = lambda pairs, suf="": ", ".join(f"`{v}{suf}`" for v, _ in pairs)
    iwt = lambda v: int(round(v)) if isinstance(v, (int, float)) else v
    dark_tinted = [(v, n2) for v, n2 in col['dark']['page_bg_common'] if v not in ("#000000", "#000")][:5]
    return f"""
## Concrete target values (measured on {n} real top-tier sites)

Not opinions, the medians and shapes of what design-led sites actually ship. Aim
inside these unless the brand gives you a reason to leave.

- **Primary button:** radius median `{bp.get('radius_px',{}).get('median')}px` (the field
  splits between soft-round 8-12px and a full pill, both fine; pills are ~{bp.get('radius_px',{}).get('pill_pct')}% of sites).
  Padding around `{bp.get('padding_y_px',{}).get('median')}px {bp.get('padding_x_px',{}).get('median')}px`,
  label `{bp.get('font_size_px',{}).get('median')}px`, weight ~`{iwt(bp.get('font_weight',{}).get('median'))}`
  (400 is common, a bold label is not required). Only ~{bp.get('with_shadow_pct')}% put a shadow on the button.
- **Type scale:** h1 median `{h1.get('font_size_px',{}).get('median')}px`, body `{body.get('font_size_px',{}).get('median')}px`.
  Headlines run a tight line-height (~`{h1.get('line_height_ratio',{}).get('median')}`) and ~{h1.get('neg_tracking_pct')}%
  negatively track; body sits at line-height ~`{body.get('line_height_ratio',{}).get('median')}` with normal tracking.
- **Layout:** content max-width median `{lay['container_max_px']['median']}px` (commonly {fmt(lay['container_max_px']['common'][:3],'px')}).
  Section vertical rhythm median `{lay['section_padding_top_px']['median']}px`.
- **Spacing:** a 4/8px grid, but not religiously, most-used steps are {fmt(c['spacing']['padding_scale_common'][:8],'px')}.
- **Light palette:** page bg almost always `#ffffff` (or a near-white); primary text a near-black, rarely pure `#000` on pure white.
  Accent is wide open, {fmt(col['light']['accent_common'][:6])} all appear once each across sites. The hue is never the tell.
- **Dark palette:** page bg is usually a *tinted* near-black ({fmt(dark_tinted)}); pure `#000000` shows up but
  is the minority. Raised surfaces are a step lighter, not a 1px border on the same color; text is an off-white, not pure `#fff`.

See `reference/COMPONENT-SPECS.md` for the full per-component tables and per-site appendix.
"""

HEADER = """<!-- AI DESIGN TELLS, drop-in design harness -->
<!-- Paste this whole block into your coding agent's system prompt, CLAUDE.md, -->
<!-- .cursorrules, or a v0/Lovable custom-instructions field. It pre-empts the -->
<!-- machine-default "AI slop" look the same way the detector scores it. -->
<!-- Generated from the AI Design Tells taxonomy, do not edit by hand. -->

# Design like a person, not the median of the training set

When you build or edit any UI, you tend to fall back to the statistical centre of
your training data: indigo gradients, Inter, a hero with three emoji cards, one
border-radius, one soft shadow, a vague headline. That look is instantly legible
as machine-made. **Make intentional choices instead.** Before you output a page,
satisfy every rule below; they are exactly what the open `aidt` linter measures
(Tell Score, 0-100, lower is better).

## The rule: one sentence of intent per dimension

For each design dimension, you must be able to state *why this and not the
default*. If your only reason is "it's modern / clean / standard," that is the
tell. Pick from the product's own brand, domain, content, and voice.

"""

CHECKLIST_INTRO = "\n## Pre-ship checklist (all must be true)\n\n"

FOOTER = """
## What 202 real top-tier sites actually do (use these as targets)

Learned by rendering 202 human-crafted sites (Stripe, Linear, Toss, Apple, Vercel,
Figma, ...) and reading their computed styles:

- **Type:** a custom or commissioned display face is the norm; if you do use Inter
  or the system stack (a quarter of top sites do, Linear included), earn it with a
  real scale and optical tracking. ~78% negatively track large headings.
- **Radius:** a *hierarchy*, not one value. Median 6 distinct radii per site (p90 = 12).
- **Sizes:** a rich scale is normal, median 10 distinct sizes (p90 = 15). The tell
  is the degenerate one-or-two-size page, not a high count.
- **Layout:** top sites almost never center everything, median 2% of blocks centered.
- **Focus:** ~96% define a visible focus state. Do too.
- **Color:** a brand purple is fine (Stripe uses 123 purple accents and reads as
  crafted). What is NOT fine is the *exact* default indigo with nothing else decided.

The rule of thumb: any one default is forgivable if real craft sits next to it.
The AI look is the *bundle* of defaults with nothing compensating.

## How to verify

Run the detector on your output and drive the Tell Score toward 0:

```bash
python src/cli.py your_page.html        # or wire up the MCP `score_design` tool
```

A score under ~12 reads as human-crafted; anything over ~45 is a strong AI-default
signature. The point is not to chase a number, it is that every number you remove
corresponds to a real decision you made on purpose.
"""


def main():
    fams = tells_by_family()
    parts = [HEADER]
    for k, tells in fams.items():
        name, blurb = FAMILIES[k]
        parts.append(f"\n## {k}. {name}, {blurb}\n")
        for t in tells:
            sev = "" if t.severity == "tell" else " _(minor)_"
            parts.append(f"- **Don't: {t.name}.**{sev} {t.why[0].upper() + t.why[1:]}.")
            parts.append(f"  **Do instead:** {t.fix}.")
    # checklist
    parts.append(CHECKLIST_INTRO)
    for t in sorted(TELLS, key=lambda x: (x.family, -x.weight)):
        parts.append(f"- [ ] **{t.family}**, {t.fix[0].upper() + t.fix[1:]}.")
    parts.append(spec_block())
    parts.append(FOOTER)
    parts.append(f"\n<!-- {len(TELLS)} tells across {len(FAMILIES)} families. "
                 f"Source of truth: src/taxonomy.py -->\n")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"wrote {OUT} ({len(TELLS)} tells)")


if __name__ == "__main__":
    main()
