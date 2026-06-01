<!-- AI DESIGN TELLS, drop-in design harness -->
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



## A. Color, Chromatic conformity

- **Don't: Indigo/violet default palette.** Indigo-500 is the single most over-represented brand color in the training corpus, so models treat purple as the default 'modern' accent.
  **Do instead:** pick a hue from the product's own brand or domain; derive a ramp in a perceptual space (LCH/OKLCH) and expose it as semantic tokens.
- **Don't: Blue->purple hero gradient.** The blue-to-purple linear gradient on a hero/button is the visual signature of v0/Lovable/Bolt output.
  **Do instead:** use a flat brand color or a restrained two-stop gradient within one hue; reserve gradients for meaning.
- **Don't: Default-ramp utilities, no semantic tokens.** _(minor)_ Scattering *-500/*-600 utilities with no --color-* tokens means color carries no system or meaning.
  **Do instead:** define semantic CSS custom properties (--color-action, --color-danger) before reaching for raw values.

## B. Type, Typographic defaulting

- **Don't: Inter/Roboto/system default font.** Inter and the system stack are the highest-frequency fonts in scraped templates; choosing them by default is the loudest type tell.
  **Do instead:** commit to one distinctive display face with personality (custom or commissioned, like Geist/Sohne) paired with a readable body face.
- **Don't: No type scale discipline.** Either an ad-hoc pile of sizes or just one or two sizes signals no modular scale and therefore no hierarchy.
  **Do instead:** use a 4-6 step modular scale; size, weight and color together build hierarchy.
- **Don't: No optical tracking on display type.** _(minor)_ Premium display type carries negative letter-spacing; leaving it at the browser default reads as untouched.
  **Do instead:** apply negative tracking to large headings (Linear uses -0.22px display / -0.11px body).

## C. Layout, Compositional cliche

- **Don't: Hero + three-feature-card template.** The hero, then a three-up icon-card grid, then a CTA is the canonical SaaS-template layout AI reproduces from tutorials.
  **Do instead:** let the content dictate structure; vary section shape, asymmetry and emphasis instead of the template.
- **Don't: Center-everything composition.** Centering nearly every block is the path of least resistance and erases the tension and rhythm of an intentional grid.
  **Do instead:** use a real grid; left-align long-form, reserve centering for genuine focal moments.
- **Don't: One border-radius everywhere.** A single radius reused on every surface (the shadcn 0.5rem default) flattens the hierarchy of nested elements.
  **Do instead:** scale radius with element size; nested radii should differ (outer larger than inner).
- **Don't: Emoji as iconography.** _(minor)_ Emoji in headings and feature cards is a hallmark of model-written marketing pages.
  **Do instead:** use a coherent icon set or custom glyphs that match the brand's weight and grid.

## D. Spacing, Undifferentiated rhythm

- **Don't: One padding token on every card.** Identical padding and gaps on every block (the 'same 24px everywhere') is undifferentiated default rhythm.
  **Do instead:** vary spacing to express grouping and importance; whitespace is the cheapest way to look designed.
- **Don't: Uniform section rhythm.** _(minor)_ Every section sharing one vertical padding means no passage of the page is emphasised over another.
  **Do instead:** modulate section spacing; give the hero and key moments more air.

## E. Surface, Depth & state defaults

- **Don't: Generic diffuse shadow.** The default soft drop shadow (Tailwind shadow-lg / 0 10px 15px rgba(0,0,0,.1)) applied to every card is an un-designed depth cue.
  **Do instead:** design elevation: tight contained shadows, or layering and hairlines instead of blur (Linear's approach).
- **Don't: Glassmorphism overuse.** _(minor)_ Backdrop-blur translucency on many surfaces is a trend the models over-apply because it is over-represented recently.
  **Do instead:** reserve blur for genuinely layered surfaces; prefer solid, high-contrast panels.
- **Don't: No hairlines / no focus-visible.** Missing 1px low-alpha separators and missing :focus-visible styles reveal that microstates and accessibility were never designed.
  **Do instead:** add designed hairlines (0.5-1px low alpha) and a visible high-contrast focus ring.

## F. Motion, Motion defaults

- **Don't: One fade applied to everything.** _(minor)_ The same entrance fade/slide on every element is the default AI motion gesture.
  **Do instead:** animate with intent; motion should follow navigation or storytelling, not decorate uniformly.
- **Don't: Missing interactive microstates.** Buttons and inputs without designed hover/focus/active/disabled states are the strongest craft tell - premium UI designs all six.
  **Do instead:** design all six microstates (default, hover, focus, active, disabled, loading) for every interactive element.
- **Don't: Uneased transitions.** _(minor)_ Transitions with no custom duration/easing snap instead of feeling considered.
  **Do instead:** define curves and durations (~150ms hover, 300ms state change) as a small motion system.

## G. Copy, Language defaults

- **Don't: Vague aspirational headline.** 'Build the future of work', 'all-in-one platform' - grammatically perfect, topically relevant, completely forgettable copy is the language signature of generated marketing.
  **Do instead:** write in a real voice with a specific, opinionated claim a founder would actually say.
- **Don't: Only generic CTAs.** _(minor)_ 'Get Started' / 'Learn More' as the sole calls to action carry no product-specific promise.
  **Do instead:** make the CTA predict what happens next in the product's own words (Toss: a button should hint at the next step).
- **Don't: Placeholder / lorem ipsum copy.** Shipped lorem ipsum or template placeholder copy means the content was never written.
  **Do instead:** write the real words; copy is UX, not filler (Toss treats text as a foundational design element).

## Pre-ship checklist (all must be true)


- [ ] **A**, Pick a hue from the product's own brand or domain; derive a ramp in a perceptual space (LCH/OKLCH) and expose it as semantic tokens.
- [ ] **A**, Use a flat brand color or a restrained two-stop gradient within one hue; reserve gradients for meaning.
- [ ] **A**, Define semantic CSS custom properties (--color-action, --color-danger) before reaching for raw values.
- [ ] **B**, Commit to one distinctive display face with personality (custom or commissioned, like Geist/Sohne) paired with a readable body face.
- [ ] **B**, Use a 4-6 step modular scale; size, weight and color together build hierarchy.
- [ ] **B**, Apply negative tracking to large headings (Linear uses -0.22px display / -0.11px body).
- [ ] **C**, Let the content dictate structure; vary section shape, asymmetry and emphasis instead of the template.
- [ ] **C**, Use a real grid; left-align long-form, reserve centering for genuine focal moments.
- [ ] **C**, Scale radius with element size; nested radii should differ (outer larger than inner).
- [ ] **C**, Use a coherent icon set or custom glyphs that match the brand's weight and grid.
- [ ] **D**, Vary spacing to express grouping and importance; whitespace is the cheapest way to look designed.
- [ ] **D**, Modulate section spacing; give the hero and key moments more air.
- [ ] **E**, Add designed hairlines (0.5-1px low alpha) and a visible high-contrast focus ring.
- [ ] **E**, Design elevation: tight contained shadows, or layering and hairlines instead of blur (Linear's approach).
- [ ] **E**, Reserve blur for genuinely layered surfaces; prefer solid, high-contrast panels.
- [ ] **F**, Design all six microstates (default, hover, focus, active, disabled, loading) for every interactive element.
- [ ] **F**, Animate with intent; motion should follow navigation or storytelling, not decorate uniformly.
- [ ] **F**, Define curves and durations (~150ms hover, 300ms state change) as a small motion system.
- [ ] **G**, Write in a real voice with a specific, opinionated claim a founder would actually say.
- [ ] **G**, Write the real words; copy is UX, not filler (Toss treats text as a foundational design element).
- [ ] **G**, Make the CTA predict what happens next in the product's own words (Toss: a button should hint at the next step).

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


<!-- 21 tells across 7 families. Source of truth: src/taxonomy.py -->
