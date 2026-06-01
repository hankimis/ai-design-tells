#!/usr/bin/env python3
"""
Generate the drop-in MD harness (harness/AI-DESIGN-TELLS.md) from the taxonomy,
so the prevention guidance can never drift from what the detector measures.

The harness is meant to be pasted into a coding agent's system prompt / CLAUDE.md
/ .cursorrules. It turns each *detected* tell into a *preventive* instruction.
"""
import os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from taxonomy import TELLS, FAMILIES, tells_by_family  # noqa: E402

OUT = os.path.join(ROOT, "harness", "AI-DESIGN-TELLS.md")

HEADER = """<!-- AI DESIGN TELLS — drop-in design harness -->
<!-- Paste this whole block into your coding agent's system prompt, CLAUDE.md, -->
<!-- .cursorrules, or a v0/Lovable custom-instructions field. It pre-empts the -->
<!-- machine-default "AI slop" look the same way the detector scores it. -->
<!-- Generated from the AI Design Tells taxonomy — do not edit by hand. -->

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
## How to verify

Run the detector on your output and drive the Tell Score toward 0:

```bash
python src/cli.py your_page.html        # or wire up the MCP `score_design` tool
```

A score under ~12 reads as human-crafted; anything over ~45 is a strong AI-default
signature. The point is not to chase a number — it is that every number you remove
corresponds to a real decision you made on purpose.
"""


def main():
    fams = tells_by_family()
    parts = [HEADER]
    for k, tells in fams.items():
        name, blurb = FAMILIES[k]
        parts.append(f"\n## {k}. {name} — {blurb}\n")
        for t in tells:
            sev = "" if t.severity == "tell" else " _(minor)_"
            parts.append(f"- **Don't: {t.name}.**{sev} {t.why[0].upper() + t.why[1:]}.")
            parts.append(f"  **Do instead:** {t.fix}.")
    # checklist
    parts.append(CHECKLIST_INTRO)
    for t in sorted(TELLS, key=lambda x: (x.family, -x.weight)):
        parts.append(f"- [ ] **{t.family}** — {t.fix[0].upper() + t.fix[1:]}.")
    parts.append(FOOTER)
    parts.append(f"\n<!-- {len(TELLS)} tells across {len(FAMILIES)} families. "
                 f"Source of truth: src/taxonomy.py -->\n")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"wrote {OUT} ({len(TELLS)} tells)")


if __name__ == "__main__":
    main()
