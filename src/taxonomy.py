"""
The AI Design Tells taxonomy, the single source of truth.

Every "tell" is a *measurable* signal that a user interface was produced by a
generative model defaulting to the median of its training distribution, rather
than designed by a person making intentional choices. The taxonomy is grounded
in (a) the documented mechanism of why AI converges on one look, (b) the
published craft rules of human-crafted top-tier interfaces, and (c) classic
design theory. Citations are attached to each tell and collected in
paper/refs.bib.

The detector in scorer.py consumes this module; the paper, the README tables,
and the harness/MCP descriptions are all generated from it, so there is exactly
one place to edit a tell.

Families
  A COLOR        chromatic conformity (the purple-gradient problem)
  B TYPE         typographic defaulting (Inter/Roboto, no scale, no tracking)
  C LAYOUT       compositional cliches (hero+3 cards, center-everything, uniform radius)
  D SPACING      undifferentiated rhythm (default tokens, no optical adjustment)
  E SURFACE      depth defaults (generic diffuse shadow, glass overuse, no hairline/focus)
  F MOTION       motion defaults (fade-everything, missing microstates, uneased)
  G COPY         language defaults (vague aspirational headline, generic CTA, hedging)

Each tell exposes a `detect(doc)` predicate returning (fired: bool, evidence: list[str]).
`doc` is a parsed Document (see scorer.py): it exposes .html, .css_text, .styles
(flattened declarations), .fonts, .colors, .text_blocks, helper queries, etc.

The headline metric is the TELL SCORE in [0, 100]: the weighted fraction of the
maximum attainable tell weight that fired. 0 = no tells (reads as human-crafted),
100 = every tell fired (maximally "on-distribution"). Lower is better.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List


@dataclass
class Tell:
    id: str
    family: str          # one of FAMILIES keys
    name: str
    weight: float        # contribution to the max attainable score
    why: str             # why this reads as machine-default
    fix: str             # the intentional alternative a designer would choose
    cite: List[str]      # bib keys in paper/refs.bib
    detect: Callable     # (doc) -> (bool, list[str])
    severity: str = "tell"   # "tell" | "smell" (smell = weak/context-dependent signal)


FAMILIES = {
    "A": ("Color", "Chromatic conformity"),
    "B": ("Type", "Typographic defaulting"),
    "C": ("Layout", "Compositional cliche"),
    "D": ("Spacing", "Undifferentiated rhythm"),
    "E": ("Surface", "Depth & state defaults"),
    "F": ("Motion", "Motion defaults"),
    "G": ("Copy", "Language defaults"),
}


# --------------------------------------------------------------------------
# Detection helpers (kept tiny and dependency-free; doc supplies parsed data)
# --------------------------------------------------------------------------

# Indigo/violet/purple family that AI models overwhelmingly default to. The hex
# anchors are the Tailwind indigo/violet/purple 400-700 ramp plus shadcn default.
PURPLE_HEXES = {
    "#6366f1", "#4f46e5", "#4338ca", "#818cf8", "#a5b4fc",   # indigo 400-700
    "#8b5cf6", "#7c3aed", "#6d28d9", "#a78bfa", "#c4b5fd",   # violet
    "#a855f7", "#9333ea", "#7e22ce", "#c084fc", "#d8b4fe",   # purple
    "#d946ef", "#c026d3",                                     # fuchsia
}
PURPLE_NAME_RE = r"\b(indigo|violet|purple|fuchsia)\b"

GENERIC_FONTS = {"inter", "roboto", "arial", "helvetica", "system-ui",
                 "-apple-system", "segoe ui", "sans-serif", "open sans", "lato"}

VAGUE_HEADLINE_RE = (
    r"\b(build the future|all[- ]in[- ]one|next[- ]generation|empower(?:ing)? your|"
    r"unlock your|supercharge|take your \w+ to the next level|seamlessly|"
    r"revolutioni[sz]e|reimagine|effortlessly|powerful (?:platform|solution)|"
    r"smarter way to|the future of|elevate your|unleash|transform the way)\b"
)
GENERIC_CTA = {"get started", "learn more", "sign up", "try for free",
               "get started for free", "start free trial", "contact us"}


def _hue_is_purple(h):
    """HSL hue (deg) in the indigo..fuchsia arc."""
    return 240 <= h <= 300


# --------------------------------------------------------------------------
# A, COLOR
# --------------------------------------------------------------------------

def _a1(doc):
    # Calibrated on 202 real sites: a *brand* purple (e.g. Stripe #635bff) is common
    # in good design and is NOT a tell. Only the exact AI-default ramp (Tailwind/
    # shadcn indigo-violet hexes) or the named utility classes discriminate.
    hits = [c for c in doc.colors if c.normalized in PURPLE_HEXES]
    cls = doc.find_classes(PURPLE_NAME_RE)
    ev = []
    if hits:
        ev.append(f"{len(hits)} exact default-indigo value(s), e.g. {hits[0].raw}")
    if cls:
        ev.append(f"default purple utility class(es): {', '.join(sorted(set(cls))[:4])}")
    fired = bool(hits or cls)
    return fired, ev


def _a2(doc):
    grads = doc.gradients_mixing_blue_and_purple()
    ev = [f"blue->purple gradient: {g[:70]}" for g in grads[:2]]
    return bool(grads), ev


def _a3(doc):
    util = doc.count_default_color_utilities()
    has_tokens = doc.has_semantic_color_tokens()
    fired = util >= 4 and not has_tokens
    ev = []
    if fired:
        ev.append(f"{util} default-ramp color utilities and no --color-* semantic tokens")
    return fired, ev


# --------------------------------------------------------------------------
# B, TYPE
# --------------------------------------------------------------------------

def _b1(doc):
    primary = doc.primary_font()
    fired = primary is not None and primary.lower() in GENERIC_FONTS
    ev = [f"primary font is '{primary}'"] if fired else []
    if fired and not doc.has_custom_font_face():
        ev.append("no @font-face / custom display face declared")
    return fired, ev


def _b2(doc):
    sizes = doc.font_sizes()
    n = len(sizes)
    if n == 0:
        return False, []
    # Calibrated on 202 real sites: the human median is 10 distinct sizes and p90 is
    # 15, so a high count is NORMAL, not "no scale". Only the degenerate low end (a
    # multi-section page with 1-2 sizes = no hierarchy) is a real tell.
    if n <= 2 and doc.has_multiple_sections():
        return True, [f"only {n} distinct font size(s) across a multi-section page (no hierarchy)"]
    if n > 18:
        return True, [f"{n} distinct font sizes (beyond any real type scale)"]
    return False, []


def _b3(doc):
    big = doc.has_large_headings()
    tracked = doc.has_negative_tracking_on_large()
    fired = big and not tracked
    ev = ["large headings with default letter-spacing (no optical tracking)"] if fired else []
    return fired, ev


# --------------------------------------------------------------------------
# C, LAYOUT
# --------------------------------------------------------------------------

def _c1(doc):
    fired = doc.has_hero_then_three_feature_cards()
    ev = ["hero section followed by a 3-up icon/feature card grid"] if fired else []
    return fired, ev


def _c2(doc):
    frac = doc.centered_block_fraction()
    fired = frac >= 0.6
    ev = [f"{frac*100:.0f}% of top-level blocks are center-aligned"] if fired else []
    return fired, ev


def _c3(doc):
    radii = doc.border_radii()
    fired = len(radii) == 1 and doc.radius_usage_count() >= 5
    ev = [f"single border-radius '{next(iter(radii))}' reused {doc.radius_usage_count()}x"] if fired else []
    return fired, ev


def _c4(doc):
    emoji = doc.emoji_in_headings_or_cards()
    fired = len(emoji) >= 2
    ev = [f"emoji used as iconography: {' '.join(emoji[:6])}"] if fired else []
    return fired, ev


# --------------------------------------------------------------------------
# D, SPACING
# --------------------------------------------------------------------------

def _d1(doc):
    dominant, frac = doc.dominant_padding()
    fired = dominant is not None and frac >= 0.7 and doc.padding_token_count() >= 4
    ev = [f"{frac*100:.0f}% of padded blocks share one value ({dominant})"] if fired else []
    return fired, ev


def _d2(doc):
    fired = doc.uniform_section_rhythm()
    ev = ["every section uses the same vertical padding (no rhythmic emphasis)"] if fired else []
    return fired, ev


# --------------------------------------------------------------------------
# E, SURFACE
# --------------------------------------------------------------------------

def _e1(doc):
    fired = doc.has_generic_diffuse_shadow()
    ev = ["default diffuse shadow (shadow-lg / 0 .. rgba(0,0,0,.1)) used uniformly"] if fired else []
    return fired, ev


def _e2(doc):
    n = doc.glass_element_count()
    fired = n >= 3
    ev = [f"backdrop-blur glassmorphism on {n} elements"] if fired else []
    return fired, ev


def _e3(doc):
    no_focus = not doc.has_focus_visible()
    no_hair = not doc.has_hairline_border()
    fired = no_focus or no_hair
    ev = []
    if no_focus:
        ev.append("no :focus-visible style (keyboard focus left to browser default)")
    if no_hair:
        ev.append("no low-alpha hairline borders (1px separators undesigned)")
    return fired, ev


# --------------------------------------------------------------------------
# F, MOTION
# --------------------------------------------------------------------------

def _f1(doc):
    fired = doc.same_animation_on_many_elements()
    ev = ["one fade/slide animation applied uniformly to many elements"] if fired else []
    return fired, ev


def _f2(doc):
    missing = doc.interactive_missing_states()
    fired = missing >= 2
    ev = [f"{missing} interactive element groups missing hover/focus/active states"] if fired else []
    return fired, ev


def _f3(doc):
    has_motion = doc.has_any_transition_or_animation()
    eased = doc.has_custom_easing_or_duration()
    fired = has_motion and not eased
    ev = ["transitions present but no custom easing/duration (snap, not designed)"] if fired else []
    return fired, ev


# --------------------------------------------------------------------------
# G, COPY
# --------------------------------------------------------------------------

def _g1(doc):
    hits = doc.match_text(VAGUE_HEADLINE_RE)
    fired = len(hits) >= 1
    ev = [f"vague aspirational phrasing: {', '.join(repr(h) for h in hits[:3])}"] if fired else []
    return fired, ev


def _g2(doc):
    btns = [c.strip().lower() for c in doc.button_texts()]
    ctas = [c for c in btns if c in GENERIC_CTA]
    fired = len(btns) > 0 and len(ctas) > 0 and all(c in GENERIC_CTA for c in btns)
    ev = [f"only generic CTAs: {', '.join(sorted(set(ctas)))}"] if fired else []
    return fired, ev


def _g3(doc):
    fired = doc.has_placeholder_copy()
    ev = ["lorem ipsum / placeholder copy present"] if fired else []
    return fired, ev


# --------------------------------------------------------------------------
# Registry
# --------------------------------------------------------------------------

TELLS: List[Tell] = [
    Tell("A1", "A", "Indigo/violet default palette", 9.0,
         "indigo-500 is the single most over-represented brand color in the training corpus, so models treat purple as the default 'modern' accent",
         "pick a hue from the product's own brand or domain; derive a ramp in a perceptual space (LCH/OKLCH) and expose it as semantic tokens",
         ["wathan_indigo", "prg_purple", "kai_purple"], _a1),
    Tell("A2", "A", "Blue->purple hero gradient", 7.0,
         "the blue-to-purple linear gradient on a hero/button is the visual signature of v0/Lovable/Bolt output",
         "use a flat brand color or a restrained two-stop gradient within one hue; reserve gradients for meaning",
         ["studio925_slop", "prg_purple"], _a2),
    Tell("A3", "A", "Default-ramp utilities, no semantic tokens", 4.0,
         "scattering *-500/*-600 utilities with no --color-* tokens means color carries no system or meaning",
         "define semantic CSS custom properties (--color-action, --color-danger) before reaching for raw values",
         ["mantlr_premium", "studio925_slop"], _a3, severity="smell"),

    Tell("B1", "B", "Inter/Roboto/system default font", 9.0,
         "Inter and the system stack are the highest-frequency fonts in scraped templates; choosing them by default is the loudest type tell",
         "commit to one distinctive display face with personality (custom or commissioned, like Geist/Sohne) paired with a readable body face",
         ["anthropic_cookbook", "studio925_slop", "mantlr_premium"], _b1),
    Tell("B2", "B", "No type scale discipline", 5.0,
         "either an ad-hoc pile of sizes or just one or two sizes signals no modular scale and therefore no hierarchy",
         "use a 4-6 step modular scale; size, weight and color together build hierarchy",
         ["refactoring_ui", "mantlr_premium"], _b2),
    Tell("B3", "B", "No optical tracking on display type", 3.0,
         "premium display type carries negative letter-spacing; leaving it at the browser default reads as untouched",
         "apply negative tracking to large headings (Linear uses -0.22px display / -0.11px body)",
         ["linear_redesign", "mantlr_premium"], _b3, severity="smell"),

    Tell("C1", "C", "Hero + three-feature-card template", 8.0,
         "the hero, then a three-up icon-card grid, then a CTA is the canonical SaaS-template layout AI reproduces from tutorials",
         "let the content dictate structure; vary section shape, asymmetry and emphasis instead of the template",
         ["prg_purple", "studio925_slop"], _c1),
    Tell("C2", "C", "Center-everything composition", 5.0,
         "centering nearly every block is the path of least resistance and erases the tension and rhythm of an intentional grid",
         "use a real grid; left-align long-form, reserve centering for genuine focal moments",
         ["refactoring_ui"], _c2),
    Tell("C3", "C", "One border-radius everywhere", 4.0,
         "a single radius reused on every surface (the shadcn 0.5rem default) flattens the hierarchy of nested elements",
         "scale radius with element size; nested radii should differ (outer larger than inner)",
         ["refactoring_ui", "studio925_slop"], _c3),
    Tell("C4", "C", "Emoji as iconography", 3.0,
         "emoji in headings and feature cards is a hallmark of model-written marketing pages",
         "use a coherent icon set or custom glyphs that match the brand's weight and grid",
         ["studio925_slop"], _c4, severity="smell"),

    Tell("D1", "D", "One padding token on every card", 5.0,
         "identical padding and gaps on every block (the 'same 24px everywhere') is undifferentiated default rhythm",
         "vary spacing to express grouping and importance; whitespace is the cheapest way to look designed",
         ["studio925_slop", "refactoring_ui"], _d1),
    Tell("D2", "D", "Uniform section rhythm", 3.0,
         "every section sharing one vertical padding means no passage of the page is emphasised over another",
         "modulate section spacing; give the hero and key moments more air",
         ["refactoring_ui", "mantlr_premium"], _d2, severity="smell"),

    Tell("E1", "E", "Generic diffuse shadow", 5.0,
         "the default soft drop shadow (Tailwind shadow-lg / 0 10px 15px rgba(0,0,0,.1)) applied to every card is an un-designed depth cue",
         "design elevation: tight contained shadows, or layering and hairlines instead of blur (Linear's approach)",
         ["linear_redesign", "mantlr_premium"], _e1),
    Tell("E2", "E", "Glassmorphism overuse", 4.0,
         "backdrop-blur translucency on many surfaces is a trend the models over-apply because it is over-represented recently",
         "reserve blur for genuinely layered surfaces; prefer solid, high-contrast panels",
         ["logrocket_linear", "studio925_slop"], _e2, severity="smell"),
    Tell("E3", "E", "No hairlines / no focus-visible", 6.0,
         "missing 1px low-alpha separators and missing :focus-visible styles reveal that microstates and accessibility were never designed",
         "add designed hairlines (0.5-1px low alpha) and a visible high-contrast focus ring",
         ["mantlr_premium", "nielsen_heuristics"], _e3),

    Tell("F1", "F", "One fade applied to everything", 4.0,
         "the same entrance fade/slide on every element is the default AI motion gesture",
         "animate with intent; motion should follow navigation or storytelling, not decorate uniformly",
         ["studio925_slop"], _f1, severity="smell"),
    Tell("F2", "F", "Missing interactive microstates", 7.0,
         "buttons and inputs without designed hover/focus/active/disabled states are the strongest craft tell - premium UI designs all six",
         "design all six microstates (default, hover, focus, active, disabled, loading) for every interactive element",
         ["mantlr_premium", "nielsen_heuristics"], _f2),
    Tell("F3", "F", "Uneased transitions", 3.0,
         "transitions with no custom duration/easing snap instead of feeling considered",
         "define curves and durations (~150ms hover, 300ms state change) as a small motion system",
         ["mantlr_premium"], _f3, severity="smell"),

    Tell("G1", "G", "Vague aspirational headline", 6.0,
         "'Build the future of work', 'all-in-one platform' - grammatically perfect, topically relevant, completely forgettable copy is the language signature of generated marketing",
         "write in a real voice with a specific, opinionated claim a founder would actually say",
         ["studio925_slop", "toss_writing"], _g1),
    Tell("G2", "G", "Only generic CTAs", 4.0,
         "'Get Started' / 'Learn More' as the sole calls to action carry no product-specific promise",
         "make the CTA predict what happens next in the product's own words (Toss: a button should hint at the next step)",
         ["toss_writing"], _g2, severity="smell"),
    Tell("G3", "G", "Placeholder / lorem ipsum copy", 5.0,
         "shipped lorem ipsum or template placeholder copy means the content was never written",
         "write the real words; copy is UX, not filler (Toss treats text as a foundational design element)",
         ["toss_writing"], _g3),
]


def max_score() -> float:
    return sum(t.weight for t in TELLS)


def tells_by_family():
    out = {k: [] for k in FAMILIES}
    for t in TELLS:
        out[t.family].append(t)
    return out
