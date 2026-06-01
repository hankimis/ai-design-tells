# DESIGN.md, pre-registration

The hypotheses, falsification conditions, and confound controls for *The Tells*,
fixed before the figures were drawn. Kept in the repo so the result can be judged
against what was promised, not what was found.

## Thesis under test

The "AI-generated design look" is **not ineffable taste** but a **finite,
enumerable set of statistical defaults**, and is therefore measurable. A
transparent, weighted detector over a single HTML document can (a) separate
machine-default pages from designed ones, and (b) quantify the effect of applying
documented design fixes while holding content constant.

## What would falsify it

- **H1 (separation).** AI-default pages score higher than designed pages with a
  clear margin. *Falsified if* the two families overlap on Tell Score, or the
  margin is within noise.
- **H2 (confound-controlled refactor).** Holding a page's product, sections, and
  information fixed and changing only tell-bearing properties lowers the Tell
  Score substantially. *Falsified if* the score barely moves, i.e. the tells are
  not what carries the look.
- **H3 (decomposition).** A small number of strong tells (color, type, layout,
  microstates) account for most of the score. *Falsified if* the score is diffuse
  across many equal small signals with no actionable priority.
- **H4 (face validity).** The families that separate hardest match the cues humans
  actually cite ("the purple," "the font," "the three cards"). *Falsified if* the
  separation is driven by signals no one perceives.

## Design

- **Corpus.** Six self-contained HTML fixtures: three AI-default (landing,
  pricing, dashboard) instantiating documented model defaults; three designed
  (landing refactor, changelog, pricing) applying the documented fixes. Fixtures,
  not scraped sites, see *Confound & honesty* below.
- **Centerpiece.** One landing page in two versions for the confound-controlled
  before/after. The "after" changes **only** font, color system, alignment/grid,
  radius hierarchy, elevation/hairlines, motion/microstates, and copy wording.
  Same product (TaskFlow), same four sections, same three capabilities, same
  information.

## Metric

Tell Score `S = 100 · Σ wₜ·fₜ / Σ wₜ ∈ [0,100]`, lower is better, over 21 tells
(max weight 109) in seven families. Deterministic; no learned component; every
point traceable to a named tell and quoted evidence. Grade bands A<12, B<28,
C<45, D<65, F≥65 are descriptive anchors only.

## Confound controls & honesty

- **Content/structure held fixed** in the refactor (the length-matching analog):
  any score change is attributable to design dimensions, not to more/less content.
- **Designed fixtures score 0 by construction**, a demonstration that the fixes
  are *sufficient* to zero the score, **not** a claim that real designed sites
  score 0. Stated plainly in the paper and README.
- **Single-document, static** detector: it does not resolve external stylesheets
  or run JS, so it under-detects on live SPAs. Declared as a limitation, not hidden.
- **Goodhart** acknowledged: the score is a floor on intentionality, gameable by
  cosmetic swaps; strong structural/microstate tells are weighted above cosmetics.

## Planned figures

1. Money-shot: before/after Tell Score (the headline).
2. Waterfall: tell-by-tell reduction, ordered by impact.
3. Families: mean per-family score, AI-default vs designed.
4. Distribution: every corpus page on one axis, the gap.
5. Heatmap: tell × page firing matrix.
6. Template gallery: the two rendered pages side by side.
   Plus animated: reveal crossfade, terminal run, waterfall build.

## Epistemics (reserved for the paper)

What "looking human" detects (intentionality made legible, not humanity); taste as
the compression of lived choices a median cannot hold; the map-vs-territory limit
of any single score; and the second-order convergence risk, if everyone optimizes
one Tell Score, the escape from the indigo mean becomes a new mean (cf. the
reflective-loop finding in *Convergence Pressure*).
