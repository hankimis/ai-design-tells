"""
scorer.py, the AI Design Tells detector.

Static analysis of a single HTML document (with its inline <style> blocks,
style="" attributes, and utility class names). Dependency-free: Python stdlib
only, so the harness runs anywhere with one command and no install.

It parses two surfaces a generative model leaves fingerprints on:

  1. Raw CSS, declarations inside <style> and style="".
  2. Utility classes, Tailwind-style class names (bg-indigo-500, rounded-lg,
     shadow-lg, p-6, ...). Models emit these far more than hand-written CSS, so
     we resolve a useful subset of Tailwind to its underlying values.

The Document object exposes the query methods that src/taxonomy.py calls. The
scoring is a transparent weighted sum: each fired tell contributes its weight;
the TELL SCORE is 100 * fired_weight / max_weight. Lower is better.

This is a *discriminator*, not a judge of beauty. A low score means "free of the
known machine-default fingerprints," not "good design." See the paper's threats
to validity.
"""

from __future__ import annotations
import re
import colorsys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

from taxonomy import TELLS, FAMILIES, max_score


# --------------------------------------------------------------------------
# Minimal Tailwind resolution (the subset models actually emit)
# --------------------------------------------------------------------------

# Color ramp -> representative hex (500/600 anchors; enough for hue + family).
_TW_COLORS = {
    "indigo": "#6366f1", "violet": "#8b5cf6", "purple": "#a855f7",
    "fuchsia": "#d946ef", "blue": "#3b82f6", "sky": "#0ea5e9",
    "cyan": "#06b6d4", "teal": "#14b8a6", "emerald": "#10b981",
    "green": "#22c55e", "lime": "#84cc16", "yellow": "#eab308",
    "amber": "#f59e0b", "orange": "#f97316", "red": "#ef4444",
    "rose": "#f43f5e", "pink": "#ec4899", "slate": "#64748b",
    "gray": "#6b7280", "zinc": "#71717a", "neutral": "#737373",
    "stone": "#78716c",
}
_TW_SPACING = {  # rem
    "0": 0, "1": 0.25, "2": 0.5, "3": 0.75, "4": 1, "5": 1.25, "6": 1.5,
    "8": 2, "10": 2.5, "12": 3, "16": 4, "20": 5, "24": 6, "32": 8,
}
_TW_RADIUS = {  # rem
    "rounded-none": 0, "rounded-sm": 0.125, "rounded": 0.25, "rounded-md": 0.375,
    "rounded-lg": 0.5, "rounded-xl": 0.75, "rounded-2xl": 1, "rounded-3xl": 1.5,
    "rounded-full": 9999,
}
_TW_TEXT = {  # font-size rem
    "text-xs": 0.75, "text-sm": 0.875, "text-base": 1, "text-lg": 1.125,
    "text-xl": 1.25, "text-2xl": 1.5, "text-3xl": 1.875, "text-4xl": 2.25,
    "text-5xl": 3, "text-6xl": 3.75, "text-7xl": 4.5, "text-8xl": 6,
}


@dataclass
class Color:
    raw: str
    normalized: str   # #rrggbb lowercased, or "" if unresolved
    hue: float        # 0-360, -1 if achromatic/unknown


def _hex_to_hue(hx: str) -> float:
    hx = hx.lstrip("#")
    if len(hx) == 3:
        hx = "".join(c * 2 for c in hx)
    if len(hx) != 6:
        return -1.0
    try:
        r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError:
        return -1.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if s < 0.08:
        return -1.0
    return h * 360


def _mk_color(raw: str) -> Color:
    raw = raw.strip()
    hx = ""
    m = re.match(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b", raw)
    if m:
        v = m.group(1).lower()
        if len(v) == 3:
            v = "".join(c * 2 for c in v)
        hx = "#" + v
    return Color(raw=raw, normalized=hx, hue=_hex_to_hue(hx) if hx else -1.0)


# --------------------------------------------------------------------------
# HTML parsing
# --------------------------------------------------------------------------

@dataclass
class Node:
    tag: str
    classes: List[str] = field(default_factory=list)
    style: str = ""
    text: str = ""
    depth: int = 0


class _Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes: List[Node] = []
        self.styles: List[str] = []
        self._in_style = False
        self._depth = 0
        self._stack: List[Node] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "style":
            self._in_style = True
            return
        n = Node(tag=tag,
                 classes=(a.get("class", "") or "").split(),
                 style=a.get("style", "") or "",
                 depth=self._depth)
        self.nodes.append(n)
        self._stack.append(n)
        if tag not in ("img", "br", "hr", "input", "meta", "link"):
            self._depth += 1

    def handle_endtag(self, tag):
        if tag == "style":
            self._in_style = False
            return
        if tag not in ("img", "br", "hr", "input", "meta", "link"):
            self._depth = max(0, self._depth - 1)
        if self._stack:
            self._stack.pop()

    def handle_data(self, data):
        if self._in_style:
            self.styles.append(data)
        elif self._stack and data.strip():
            self._stack[-1].text += data


# CSS rule: (selector, {prop: val})
def _parse_css(css: str) -> List[Tuple[str, Dict[str, str]]]:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel = m.group(1).strip()
        body = {}
        for decl in m.group(2).split(";"):
            if ":" in decl:
                p, v = decl.split(":", 1)
                body[p.strip().lower()] = v.strip()
        rules.append((sel, body))
    return rules


_EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F0FF←-⇿⬀-⯿]"
)


class Document:
    def __init__(self, html: str):
        self.html = html
        p = _Collector()
        p.feed(html)
        self.nodes = p.nodes
        self.css_text = "\n".join(p.styles)
        self.rules = _parse_css(self.css_text)
        # All declaration bodies (rules + inline style attrs), flattened.
        self.decls: List[Dict[str, str]] = [b for _, b in self.rules]
        for n in self.nodes:
            if n.style:
                b = {}
                for decl in n.style.split(";"):
                    if ":" in decl:
                        pp, vv = decl.split(":", 1)
                        b[pp.strip().lower()] = vv.strip()
                self.decls.append(b)
        self.all_classes = [c for n in self.nodes for c in n.classes]
        self._css_lower = self.css_text.lower()
        self.vars = self._collect_vars()
        self.colors = self._collect_colors()

    def _collect_vars(self) -> Dict[str, str]:
        out = {}
        for b in self.decls:
            for k, v in b.items():
                if k.startswith("--"):
                    out[k] = v
        return out

    def _resolve(self, value: str) -> str:
        """Textually expand var(--x) references one level (enough for our checks)."""
        def sub(m):
            name = m.group(1).strip()
            return self.vars.get(name, m.group(0))
        return re.sub(r"var\(\s*(--[\w-]+)\s*(?:,[^)]*)?\)", sub, value)

    # ---- helpers ----
    def _values(self, prop: str) -> List[str]:
        out = []
        for b in self.decls:
            if prop in b:
                out.append(b[prop])
        return out

    def _all_values(self) -> str:
        return " ".join(v for b in self.decls for v in b.values())

    def _collect_colors(self) -> List[Color]:
        cols = []
        # from CSS hex
        for hx in re.findall(r"#[0-9a-fA-F]{3,6}\b", self.css_text):
            cols.append(_mk_color(hx))
        # from inline styles
        for n in self.nodes:
            for hx in re.findall(r"#[0-9a-fA-F]{3,6}\b", n.style):
                cols.append(_mk_color(hx))
        # from tailwind color utilities
        for cls in self.all_classes:
            m = re.match(r"(?:bg|text|from|via|to|border|ring)-([a-z]+)-\d{2,3}$", cls)
            if m and m.group(1) in _TW_COLORS:
                cols.append(_mk_color(_TW_COLORS[m.group(1)]))
        return cols

    # ---- A: color ----
    def find_classes(self, regex: str) -> List[str]:
        rx = re.compile(regex)
        return [c for c in self.all_classes if rx.search(c)]

    def gradients_mixing_blue_and_purple(self) -> List[str]:
        out = []
        # CSS gradients
        for v in re.findall(r"linear-gradient\([^)]*\)", self._css_lower) + \
                 re.findall(r"linear-gradient\([^)]*\)", " ".join(n.style.lower() for n in self.nodes)):
            hues = [c.hue for c in (_mk_color(h) for h in re.findall(r"#[0-9a-fA-F]{3,6}", v)) if c.hue >= 0]
            if any(200 <= h <= 240 for h in hues) and any(255 <= h <= 300 for h in hues):
                out.append(v)
        # tailwind gradient utilities: from-blue/indigo via/to-purple/violet
        fams = set()
        for cls in self.all_classes:
            m = re.match(r"(?:from|via|to)-([a-z]+)-\d{2,3}$", cls)
            if m:
                fams.add(m.group(1))
        blue = {"blue", "sky", "cyan"} & fams
        purp = {"indigo", "violet", "purple", "fuchsia"} & fams
        grad_dir = any(c.startswith("bg-gradient") or c.startswith("bg-linear") for c in self.all_classes)
        if blue and purp and grad_dir:
            out.append(f"tailwind gradient {sorted(blue)}->{sorted(purp)}")
        elif purp and grad_dir and any(c.startswith("from-") for c in self.all_classes):
            # purple-dominant gradient still counts as the signature
            out.append(f"tailwind gradient ->{sorted(purp)}")
        return out

    def count_default_color_utilities(self) -> int:
        return sum(1 for c in self.all_classes
                   if re.match(r"(?:bg|text|border|ring)-[a-z]+-\d{2,3}$", c))

    def has_semantic_color_tokens(self) -> bool:
        return bool(re.search(r"--(?:color|brand|accent|action|surface|fg|bg|danger|primary)[\w-]*\s*:", self._css_lower))

    # ---- B: type ----
    def primary_font(self) -> Optional[str]:
        # First body/:root/html font-family stack's first family.
        cands = []
        for sel, b in self.rules:
            if "font-family" in b and re.search(r"\b(body|html|:root|\*)\b", sel):
                cands.insert(0, b["font-family"])
            elif "font-family" in b:
                cands.append(b["font-family"])
        if not cands:
            # tailwind font utilities
            if any(c in ("font-sans", "antialiased") for c in self.all_classes) and \
               not any(c.startswith("font-[") for c in self.all_classes):
                return "inter"  # tailwind font-sans defaults to a system/Inter-like stack
            return None
        first = cands[0].split(",")[0].strip().strip('"\'').lower()
        return first

    def has_custom_font_face(self) -> bool:
        if "@font-face" in self._css_lower:
            return True
        # tailwind arbitrary font or a google-fonts link with a display face
        if any(c.startswith("font-[") for c in self.all_classes):
            return True
        if re.search(r"fonts\.googleapis|fonts\.gstatic|typekit|font\.", self.html.lower()):
            # a linked face counts only if it's not Inter/Roboto
            linked = re.findall(r"family=([A-Za-z+]+)", self.html)
            return any(f.lower().replace("+", " ") not in
                       {"inter", "roboto", "open sans", "lato"} for f in linked)
        return False

    def font_sizes(self) -> set:
        sizes = set(self._values("font-size"))
        for c in self.all_classes:
            if c in _TW_TEXT:
                sizes.add(f"{_TW_TEXT[c]}rem")
        return sizes

    def has_multiple_sections(self) -> bool:
        return sum(1 for n in self.nodes if n.tag in ("section", "header", "footer", "main", "article")) >= 2 \
            or self.html.lower().count("<section") >= 2

    def has_large_headings(self) -> bool:
        for c in self.all_classes:
            if c in _TW_TEXT and _TW_TEXT[c] >= 2.25:  # >= text-4xl
                return True
        for v in self.font_sizes():
            m = re.match(r"([\d.]+)rem", v)
            if m and float(m.group(1)) >= 2.25:
                return True
            m = re.match(r"([\d.]+)px", v)
            if m and float(m.group(1)) >= 36:
                return True
        return False

    def has_negative_tracking_on_large(self) -> bool:
        if any(c in ("tracking-tight", "tracking-tighter") for c in self.all_classes):
            return True
        for v in self._values("letter-spacing"):
            if v.strip().startswith("-"):
                return True
        return False

    # ---- C: layout ----
    def has_hero_then_three_feature_cards(self) -> bool:
        h = self.html.lower()
        has_hero = ("hero" in h) or bool(re.search(r"<(section|header)[^>]*>.*?<h1", h, re.S))
        # a 3-column grid of cards
        three_grid = bool(re.search(r"grid-cols-3|repeat\(3,", h)) or \
            (h.count('class="card') >= 3) or (h.count("feature") >= 3)
        return has_hero and three_grid

    def centered_block_fraction(self) -> float:
        blocks = [n for n in self.nodes if n.tag in ("section", "div", "header", "main", "article")
                  and n.depth <= 3]
        if not blocks:
            return 0.0
        centered = 0
        for n in blocks:
            cl = " ".join(n.classes)
            if "text-center" in n.classes or "items-center" in n.classes or \
               "mx-auto" in n.classes or "text-align:center" in n.style.replace(" ", "").lower() or \
               "justify-center" in n.classes:
                centered += 1
        return centered / len(blocks)

    def border_radii(self) -> set:
        radii = set(self._values("border-radius"))
        for c in self.all_classes:
            if c in _TW_RADIUS:
                radii.add(f"{_TW_RADIUS[c]}rem")
        return radii

    def radius_usage_count(self) -> int:
        n = sum(1 for c in self.all_classes if c in _TW_RADIUS)
        n += len(self._values("border-radius"))
        return n

    def emoji_in_headings_or_cards(self) -> List[str]:
        found = []
        for n in self.nodes:
            if n.tag in ("h1", "h2", "h3", "h4", "button", "a", "span", "div", "p"):
                found += _EMOJI_RE.findall(n.text)
        return found

    # ---- D: spacing ----
    def _padding_values(self) -> List[str]:
        vals = []
        for c in self.all_classes:
            m = re.match(r"p-(\d{1,2})$", c)
            if m and m.group(1) in _TW_SPACING:
                vals.append(f"{_TW_SPACING[m.group(1)]}rem")
        vals += self._values("padding")
        return vals

    def dominant_padding(self) -> Tuple[Optional[str], float]:
        vals = self._padding_values()
        if not vals:
            return None, 0.0
        from collections import Counter
        c = Counter(vals)
        top, cnt = c.most_common(1)[0]
        return top, cnt / len(vals)

    def padding_token_count(self) -> int:
        return len(self._padding_values())

    def uniform_section_rhythm(self) -> bool:
        ys = []
        for n in self.nodes:
            if n.tag in ("section", "header", "footer"):
                for c in n.classes:
                    m = re.match(r"py-(\d{1,2})$", c)
                    if m:
                        ys.append(m.group(1))
        return len(ys) >= 3 and len(set(ys)) == 1

    # ---- E: surface ----
    def has_generic_diffuse_shadow(self) -> bool:
        n = sum(1 for c in self.all_classes if c in ("shadow-lg", "shadow-xl", "shadow-2xl", "shadow-md"))
        if n >= 3:
            return True
        diffuse = 0
        for v in self._values("box-shadow"):
            if re.search(r"rgba\(0,\s*0,\s*0,\s*0?\.0?[12]\d*\)", v.replace(" ", "")) or "0,0,0,0.1" in v.replace(" ", ""):
                diffuse += 1
        return diffuse >= 3

    def glass_element_count(self) -> int:
        n = sum(1 for c in self.all_classes if c.startswith("backdrop-blur"))
        n += sum(1 for v in self._values("backdrop-filter") if "blur" in v)
        n += sum(1 for b in self.decls for k, v in b.items() if k == "-webkit-backdrop-filter" and "blur" in v)
        return n

    def has_focus_visible(self) -> bool:
        if ":focus-visible" in self._css_lower or ":focus" in self._css_lower:
            return True
        return any(c.startswith("focus-visible:") or c.startswith("focus:") for c in self.all_classes)

    def has_hairline_border(self) -> bool:
        bvals = (self._values("border") + self._values("border-top") +
                 self._values("border-bottom") + self._values("border-color"))
        for v in bvals:
            rv = self._resolve(v)
            if "rgba" in rv or "hsla" in rv or re.search(r"/\s*[\d.]+\)?", rv) or "/" in v:
                return True
        # tailwind low-alpha border: border-white/10, border-black/5
        if any(re.match(r"border-(?:white|black|[a-z]+)-?\d*\/\d+$", c) or ("/" in c and c.startswith("border-"))
               for c in self.all_classes):
            return True
        return False

    # ---- F: motion ----
    def same_animation_on_many_elements(self) -> bool:
        n = sum(1 for c in self.all_classes if c in ("animate-fade-in", "animate-fadeIn", "fade-in") or
                c.startswith("animate-fade"))
        # count elements with the same inline/animation name
        names = [v.split()[0] for v in self._values("animation") if v.strip()]
        from collections import Counter
        if names:
            top = Counter(names).most_common(1)[0][1]
            if top >= 4:
                return True
        return n >= 4

    def interactive_missing_states(self) -> int:
        interactive = [n for n in self.nodes if n.tag in ("button", "a", "input", "select", "textarea")]
        # If there is no hover/focus styling at all but interactive elements exist
        has_hover = (":hover" in self._css_lower) or any("hover:" in c for c in self.all_classes)
        has_focus = self.has_focus_visible()
        has_active = (":active" in self._css_lower) or any("active:" in c for c in self.all_classes)
        groups_missing = 0
        if interactive:
            if not has_hover:
                groups_missing += 1
            if not has_focus:
                groups_missing += 1
            if not has_active:
                groups_missing += 1
        return groups_missing

    def has_any_transition_or_animation(self) -> bool:
        if self._values("transition") or self._values("animation") or self._values("transition-property"):
            return True
        return any(c.startswith("transition") or c.startswith("animate-") for c in self.all_classes)

    def has_custom_easing_or_duration(self) -> bool:
        for v in self._values("transition") + self._values("transition-timing-function") + \
                self._values("transition-duration") + self._values("animation"):
            rv = self._resolve(v)
            if ("cubic-bezier" in rv or re.search(r"\d+\s*ms", rv) or re.search(r"\b\d*\.?\d+s\b", rv)
                    or "ease-in-out" in rv or "ease-out" in rv or "spring" in rv):
                return True
        if any(c.startswith("duration-") or c.startswith("ease-") for c in self.all_classes):
            return True
        return False

    # ---- G: copy ----
    def _visible_text(self) -> str:
        return " ".join(n.text for n in self.nodes).lower()

    def match_text(self, regex: str) -> List[str]:
        return re.findall(regex, self._visible_text(), flags=re.I)

    def button_texts(self) -> List[str]:
        out = []
        for n in self.nodes:
            if n.tag in ("button", "a"):
                t = n.text.strip()
                if t:
                    out.append(t)
        return out

    def has_placeholder_copy(self) -> bool:
        return "lorem ipsum" in self._visible_text() or "dolor sit amet" in self._visible_text()


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------

@dataclass
class TellResult:
    id: str
    family: str
    name: str
    weight: float
    severity: str
    fired: bool
    evidence: List[str]
    fix: str


@dataclass
class Report:
    score: float                 # 0-100, lower is better
    fired_weight: float
    max_weight: float
    results: List[TellResult]
    family_scores: Dict[str, float]

    @property
    def grade(self) -> str:
        s = self.score
        if s < 12:
            return "A, reads as human-crafted"
        if s < 28:
            return "B, mostly intentional, a few tells"
        if s < 45:
            return "C, visibly templated"
        if s < 65:
            return "D, strong AI-default signature"
        return "F, textbook AI slop"


def score_document(html: str) -> Report:
    doc = Document(html)
    results = []
    fired_weight = 0.0
    fam_fired = {k: 0.0 for k in FAMILIES}
    fam_max = {k: 0.0 for k in FAMILIES}
    for t in TELLS:
        fam_max[t.family] += t.weight
        fired, ev = t.detect(doc)
        if fired:
            fired_weight += t.weight
            fam_fired[t.family] += t.weight
        results.append(TellResult(t.id, t.family, t.name, t.weight, t.severity, fired, ev, t.fix))
    mx = max_score()
    family_scores = {k: (100 * fam_fired[k] / fam_max[k] if fam_max[k] else 0.0) for k in FAMILIES}
    return Report(score=100 * fired_weight / mx, fired_weight=fired_weight,
                  max_weight=mx, results=results, family_scores=family_scores)
