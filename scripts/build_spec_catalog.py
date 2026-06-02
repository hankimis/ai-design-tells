#!/usr/bin/env python3
"""
build_spec_catalog.py, aggregate data/sites_detail/*.json into a reference catalog.

Produces two artifacts:
  data/spec_catalog.json        machine-readable aggregate (medians, ranges, distributions)
  reference/COMPONENT-SPECS.md  human-readable: what real top-tier sites actually ship for
                                buttons, type, layout, spacing, color, and dark mode.

The point: instead of "don't look AI," give concrete, evidence-backed target values
pulled from N human-crafted sites, component by component.
"""
import os, sys, json, glob, statistics as st
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DETAIL = os.path.join(ROOT, "data", "sites_detail")
OUT_JSON = os.path.join(ROOT, "data", "spec_catalog.json")
OUT_MD = os.path.join(ROOT, "reference", "COMPONENT-SPECS.md")


def load():
    recs = []
    for f in sorted(glob.glob(os.path.join(DETAIL, "*.json"))):
        try:
            d = json.load(open(f))
            if d.get("ok"):
                recs.append(d)
        except Exception:
            pass
    return recs


def px(v):
    try:
        if isinstance(v, str):
            v = v.replace("px", "").strip()
        return round(float(v), 1)
    except Exception:
        return None


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 1) if xs else None


def rng(xs, lo=10, hi=90):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return (None, None)
    n = len(xs)
    return (xs[max(0, int(n * lo / 100) - 0)], xs[min(n - 1, int(n * hi / 100))])


def common(xs, n=6):
    return Counter(x for x in xs if x is not None).most_common(n)


def base_unit(scale_vals):
    """Guess the spacing base unit: are values mostly multiples of 4 or 8?"""
    vals = [v for v in scale_vals if v and v >= 4]
    if not vals:
        return None
    mult4 = sum(1 for v in vals if abs(v - round(v / 4) * 4) < 0.6)
    mult8 = sum(1 for v in vals if abs(v - round(v / 8) * 8) < 0.6)
    return {"of_4_pct": round(100 * mult4 / len(vals)), "of_8_pct": round(100 * mult8 / len(vals))}


def radius_bucket(v):
    if v is None:
        return None
    if v >= 100:
        return "pill"
    if v == 0:
        return "sharp (0)"
    if v <= 6:
        return "small (1-6)"
    if v <= 12:
        return "medium (8-12)"
    return "large (14+)"


def agg_buttons(recs):
    out = {}
    for role in ("primary", "secondary", "ghost"):
        radii, buckets, padx, pady, fsz, fw, shadows, upper, examples = [], [], [], [], [], [], 0, 0, []
        tot = 0
        for r in recs:
            for b in r.get("light", {}).get("buttons", {}).get(role, [])[:1]:  # 1 representative per site
                tot += 1
                rv = px(b.get("radius"))
                buckets.append(radius_bucket(rv))
                if rv is not None and rv < 100:   # exclude pills from the numeric median/range
                    radii.append(rv)
                pad = (b.get("padding") or "").split()
                if len(pad) == 4:
                    pady.append(px(pad[0]))
                    padx.append(px(pad[1]))
                fsz.append(px(b.get("font_size")))
                try:
                    fw.append(int(b.get("font_weight")))
                except Exception:
                    pass
                if b.get("shadow") and b["shadow"] != "none":
                    shadows += 1
                if b.get("text_transform") == "uppercase":
                    upper += 1
                if len(examples) < 8 and b.get("bg"):
                    examples.append({"site": r["name"], "bg": b.get("bg"), "color": b.get("color"),
                                     "radius": b.get("radius"), "padding": b.get("padding"),
                                     "font_size": b.get("font_size"), "font_weight": b.get("font_weight")})
        if not tot:
            continue
        out[role] = {
            "n_sites": tot,
            "radius_px": {"median": med(radii), "range": rng(radii),
                          "common": common([round(x) for x in radii if x is not None]),
                          "buckets": common(buckets, 6), "pill_pct": round(100 * buckets.count("pill") / tot) if tot else 0},
            "padding_x_px": {"median": med(padx), "range": rng(padx)},
            "padding_y_px": {"median": med(pady), "range": rng(pady)},
            "font_size_px": {"median": med(fsz), "common": common([round(x) for x in fsz if x is not None])},
            "font_weight": {"median": med(fw), "common": common(fw)},
            "with_shadow_pct": round(100 * shadows / tot),
            "uppercase_pct": round(100 * upper / tot),
            "examples": examples,
        }
    return out


def agg_typography(recs):
    out = {}
    for tag in ("h1", "h2", "h3", "h4", "body"):
        sizes, weights, lh, track_neg, families = [], [], [], 0, [],
        tot = 0
        for r in recs:
            t = r.get("light", {}).get("typography", {}).get(tag)
            if not t:
                continue
            tot += 1
            sizes.append(px(t.get("font_size_px") or t.get("font_size")))
            try:
                weights.append(int(t.get("font_weight")))
            except Exception:
                pass
            if t.get("line_height_ratio"):
                lh.append(t["line_height_ratio"])
            ls = t.get("letter_spacing")
            if ls and ls != "normal" and px(ls) is not None and px(ls) < -0.1:
                track_neg += 1
            if t.get("font_family"):
                families.append(t["font_family"].lower())
        if not tot:
            continue
        out[tag] = {
            "n_sites": tot,
            "font_size_px": {"median": med(sizes), "range": rng(sizes), "common": common([round(x) for x in sizes if x is not None])},
            "font_weight": {"median": med(weights), "common": common(weights)},
            "line_height_ratio": {"median": med(lh), "range": rng(lh)},
            "neg_tracking_pct": round(100 * track_neg / tot),
            "top_families": common(families, 8),
        }
    return out


def agg_layout(recs):
    containers, gaps, secpad, gridcols = [], [], [], []
    for r in recs:
        L = r.get("light", {}).get("layout", {})
        for c in L.get("containers", [])[:2]:
            containers.append(px(c.get("value")))
        for g in L.get("gaps", []):
            gaps.append(px(g.get("value")))
        for s in L.get("section_padding_top", [])[:3]:
            secpad.append(px(s.get("value")))
        for gc in L.get("grid_columns", [])[:2]:
            gridcols.append(gc.get("value"))
    return {
        "container_max_px": {"median": med(containers), "common": common([round(x) for x in containers if x is not None])},
        "gap_px": {"common": common([round(x) for x in gaps if x is not None], 10)},
        "section_padding_top_px": {"median": med(secpad), "common": common([round(x) for x in secpad if x is not None], 8)},
        "grid_columns": {"common": common(gridcols, 8)},
    }


def agg_spacing(recs):
    pad, mar = [], []
    for r in recs:
        S = r.get("light", {}).get("spacing", {})
        for p in S.get("padding_scale", []):
            pad.append(px(p.get("value")))
        for m in S.get("margin_scale", []):
            mar.append(px(m.get("value")))
    return {
        "padding_scale_common": common([round(x) for x in pad if x is not None], 14),
        "margin_scale_common": common([round(x) for x in mar if x is not None], 14),
        "base_unit_padding": base_unit(pad),
    }


def agg_color(recs):
    light_bg, light_text, accents = [], [], []
    dark_bg, dark_text, dark_surface = [], [], []
    n_dark = 0
    for r in recs:
        L = r.get("light", {}).get("color", {})
        if L.get("page_bg"):
            light_bg.append(L["page_bg"].lower())
        if L.get("text"):
            light_text.append(L["text"][0]["value"].lower())
        for a in L.get("accents", [])[:1]:
            accents.append(a["value"].lower())
        if r.get("has_dark_mode"):
            n_dark += 1
            D = r.get("dark", {}).get("color", {})
            if D.get("page_bg"):
                dark_bg.append(D["page_bg"].lower())
            if D.get("text"):
                dark_text.append(D["text"][0]["value"].lower())
            bgs = D.get("backgrounds", [])
            if len(bgs) > 1:
                dark_surface.append(bgs[1]["value"].lower())
    return {
        "n_total": len(recs),
        "n_dark_mode": n_dark,
        "light": {
            "page_bg_common": common(light_bg, 8),
            "primary_text_common": common(light_text, 8),
            "accent_common": common(accents, 12),
        },
        "dark": {
            "page_bg_common": common(dark_bg, 10),
            "primary_text_common": common(dark_text, 8),
            "surface_common": common(dark_surface, 8),
        },
    }


def build():
    recs = load()
    cat = {
        "n_sites": len(recs),
        "sites": sorted(r["name"] for r in recs),
        "buttons": agg_buttons(recs),
        "typography": agg_typography(recs),
        "layout": agg_layout(recs),
        "spacing": agg_spacing(recs),
        "color": agg_color(recs),
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(cat, open(OUT_JSON, "w"), indent=2, ensure_ascii=False)
    print(f"wrote {OUT_JSON} ({len(recs)} sites)")
    write_md(cat, recs)
    return cat


def _fmt_common(pairs, suffix=""):
    return ", ".join(f"`{v}{suffix}` ({c})" for v, c in pairs)


def write_md(cat, recs):
    n = cat["n_sites"]
    L = []
    L.append("# Component specs from real top-tier sites\n")
    L.append(f"What {n} human-crafted, design-led sites actually ship, read straight off their "
             "live computed styles (light and dark). Use these as concrete targets, not vibes. "
             "Every number below is measured, not asserted.\n")
    L.append(f"> Method: headless Chrome renders each site, waits for CSS and webfonts, then reads "
             f"computed styles per component, once under `prefers-color-scheme: light` and once under "
             f"`dark`. Source: `src/scrape_detail.py`, aggregated by `scripts/build_spec_catalog.py`. "
             f"Corpus: {n} sites.\n")

    # BUTTONS
    L.append("## Buttons\n")
    L.append("| Role | Radius (non-pill median / range) | Pill % | Padding y x | Font size | Font weight | Has shadow | Uppercase |")
    L.append("|---|---|---|---|---|---|---|---|")
    for role in ("primary", "secondary", "ghost"):
        b = cat["buttons"].get(role)
        if not b:
            continue
        rad = b["radius_px"]
        L.append(f"| **{role}** ({b['n_sites']}) | "
                 f"{rad['median']}px / {rad['range'][0]}–{rad['range'][1]}px | "
                 f"{rad['pill_pct']}% | "
                 f"{b['padding_y_px']['median']}px {b['padding_x_px']['median']}px | "
                 f"{b['font_size_px']['median']}px | "
                 f"{b['font_weight']['median']} | "
                 f"{b['with_shadow_pct']}% | {b['uppercase_pct']}% |")
    L.append("")
    pr = cat["buttons"].get("primary", {})
    if pr.get("radius_px", {}).get("buckets"):
        L.append(f"Primary-button radius shape: {_fmt_common(pr['radius_px']['buckets'])}. "
                 f"So the field splits between a soft-rounded look (8-12px) and a full pill; sharp 0px "
                 f"corners are a deliberate minority. Font weight clusters at "
                 f"{_fmt_common(pr['font_weight']['common'])} (note 400 is common, a heavy button label is not required).\n")
    if pr.get("examples"):
        L.append("Real primary buttons (bg / text / radius / padding):\n")
        for e in pr["examples"][:8]:
            L.append(f"- **{e['site']}**: `{e['bg']}` on `{e['color']}`, radius `{e['radius']}`, "
                     f"padding `{e['padding']}`, weight `{e['font_weight']}`")
        L.append("")

    # TYPOGRAPHY
    L.append("## Typography\n")
    L.append("| Element | Size (median / range) | Weight | Line-height ratio | Negative tracking |")
    L.append("|---|---|---|---|---|")
    for tag in ("h1", "h2", "h3", "h4", "body"):
        t = cat["typography"].get(tag)
        if not t:
            continue
        s = t["font_size_px"]
        lh = t["line_height_ratio"]
        L.append(f"| **{tag}** ({t['n_sites']}) | "
                 f"{s['median']}px / {s['range'][0]}–{s['range'][1]}px | "
                 f"{t['font_weight']['median']} | "
                 f"{lh['median']} ({lh['range'][0]}–{lh['range'][1]}) | "
                 f"{t['neg_tracking_pct']}% |")
    L.append("")
    h1 = cat["typography"].get("h1", {})
    if h1.get("top_families"):
        L.append(f"Most common h1 typefaces: {_fmt_common(h1['top_families'])}.\n")
    body = cat["typography"].get("body", {})
    if body.get("font_size_px", {}).get("common"):
        L.append(f"Body text size clusters at {_fmt_common(body['font_size_px']['common'], 'px')}. "
                 f"Line-height ratio centers on {body['line_height_ratio']['median']}.\n")

    # LAYOUT
    L.append("## Layout\n")
    lay = cat["layout"]
    L.append(f"- **Content container max-width:** median `{lay['container_max_px']['median']}px`; "
             f"common values {_fmt_common(lay['container_max_px']['common'], 'px')}.")
    L.append(f"- **Section vertical rhythm (padding-top):** median `{lay['section_padding_top_px']['median']}px`; "
             f"common {_fmt_common(lay['section_padding_top_px']['common'], 'px')}.")
    L.append(f"- **Grid columns:** {_fmt_common(lay['grid_columns']['common'])}.")
    L.append(f"- **Gaps:** {_fmt_common(lay['gap_px']['common'], 'px')}.\n")

    # SPACING
    L.append("## Spacing scale\n")
    sp = cat["spacing"]
    bu = sp["base_unit_padding"]
    if bu:
        L.append(f"Padding values are {bu['of_8_pct']}% multiples of 8 and {bu['of_4_pct']}% multiples of 4. "
                 f"The 4/8 px grid is real, but note it is not absolute, designers break it deliberately.\n")
    L.append(f"- **Padding scale (most used):** {_fmt_common(sp['padding_scale_common'], 'px')}.")
    L.append(f"- **Margin scale (most used):** {_fmt_common(sp['margin_scale_common'], 'px')}.\n")

    # COLOR
    L.append("## Color, light mode\n")
    c = cat["color"]
    L.append(f"- **Page background:** {_fmt_common(c['light']['page_bg_common'])}.")
    L.append(f"- **Primary text:** {_fmt_common(c['light']['primary_text_common'])}.")
    L.append(f"- **Accent (primary action) colors:** {_fmt_common(c['light']['accent_common'])}.\n")
    L.append("Note the accent spread: there is no single \"correct\" brand color. The tell is never the "
             "hue itself, it is reaching for the framework-default indigo with nothing else decided.\n")

    L.append("## Color, dark mode\n")
    L.append(f"{c['n_dark_mode']} of {c['n_total']} sites repaint automatically when the OS asks for dark "
             f"(`prefers-color-scheme: dark`). The rest either ship light-only, are dark by default, or "
             f"gate dark behind a manual in-page toggle this scrape did not click, so treat {c['n_dark_mode']} "
             f"as a floor, not the share of sites that support dark at all.\n")
    L.append(f"- **Dark page background:** {_fmt_common(c['dark']['page_bg_common'])}.")
    L.append(f"- **Dark primary text:** {_fmt_common(c['dark']['primary_text_common'])}.")
    L.append(f"- **Dark surface (raised panel):** {_fmt_common(c['dark']['surface_common'])}.\n")
    L.append("Dark backgrounds are almost never pure `#000000`; the norm is a near-black with a faint "
             "cool or warm tint, and surfaces are a step lighter, not a border away. Pure black on pure "
             "white text is itself a tell.\n")

    # APPENDIX
    L.append("## Appendix: per-site primary button + headline\n")
    L.append("| Site | Primary btn bg | Radius | h1 size | h1 weight | Dark mode |")
    L.append("|---|---|---|---|---|---|")
    for r in sorted(recs, key=lambda x: x["name"]):
        lb = r.get("light", {}).get("buttons", {}).get("primary", [])
        h1 = r.get("light", {}).get("typography", {}).get("h1", {})
        bg = lb[0]["bg"] if lb else "-"
        rad = lb[0]["radius"] if lb else "-"
        L.append(f"| {r['name']} | `{bg}` | {rad} | "
                 f"{h1.get('font_size','-')} | {h1.get('font_weight','-')} | "
                 f"{'yes' if r.get('has_dark_mode') else 'no'} |")
    L.append("")
    L.append(f"<!-- generated by scripts/build_spec_catalog.py from {n} sites -->")

    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    open(OUT_MD, "w", encoding="utf-8").write("\n".join(L))
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    build()
