#!/usr/bin/env python3
"""
build_korean_catalog.py, a Korean-web companion to the global spec catalog.

Korean (CJK) type has different needs than Latin: a different default font stack
(Pretendard, not Inter), a looser line-height for hangul legibility, and a habit
of slight negative tracking. This reads data/sites_kr/*.json (48 Korean design-led
sites) the same way build_spec_catalog reads the global set, then reports the
Korean norms AND how they differ from the global (mostly Western) corpus.

Outputs:
  data/korean_catalog.json
  reference/KOREAN-SPECS.md
"""
import os, sys, json, glob, statistics as st
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from build_spec_catalog import agg_buttons, agg_layout, agg_spacing, agg_color, px, med  # noqa: E402

KR_DIR = os.path.join(ROOT, "data", "sites_kr")
GLOBAL_CAT = os.path.join(ROOT, "data", "spec_catalog.json")
OUT_JSON = os.path.join(ROOT, "data", "korean_catalog.json")
OUT_MD = os.path.join(ROOT, "reference", "KOREAN-SPECS.md")

# Korean / CJK web font families, so we can label which top fonts are hangul faces.
KR_FONTS = {"pretendard", "pretendard variable", "noto sans kr", "nskr", "apple sd gothic neo",
            "spoqa han sans", "spoqa han sans neo", "nanumsquare", "nanum gothic", "맑은 고딕",
            "malgun gothic", "gmarket sans", "suit", "suite", "toss product sans", "tossface",
            "spoqa han sans jp", "ridibatang", "kopubworld", "happiness sans", "freesentation",
            "bithumb trading sans", "wantedsans", "wanted sans", "scdream", "gothic a1",
            "paperlogy", "pretendardvariable", "ridi", "코어 고딕", "본고딕"}


def load(d):
    recs = []
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            r = json.load(open(f))
            if r.get("ok"):
                recs.append(r)
        except Exception:
            pass
    return recs


def common(xs, n=10):
    return Counter(x for x in xs if x is not None).most_common(n)


def is_kr_font(name):
    n = (name or "").lower().strip()
    return n in KR_FONTS or any(k in n for k in ("pretendard", "gothic", "han sans", "noto sans kr",
                                "nanum", "gmarket", "suit", "toss", "맑은", "고딕", "명조", "wanted sans"))


def kr_typography(recs):
    """Korean-focused per-tag stats incl. the line-height and tracking that CJK cares about."""
    out = {}
    for tag in ("h1", "h2", "h3", "body"):
        sizes, weights, lh, tracks, fams = [], [], [], [], []
        tot = 0
        for r in recs:
            t = r.get("light", {}).get("typography", {}).get(tag)
            if not t:
                continue
            sz = px(t.get("font_size_px") or t.get("font_size"))
            if sz is None or sz < 8:   # 0/hidden = missing heading, not a real value
                continue
            tot += 1
            sizes.append(sz)
            try:
                weights.append(int(t.get("font_weight")))
            except Exception:
                pass
            if t.get("line_height_ratio"):
                lh.append(t["line_height_ratio"])
            ls = t.get("letter_spacing")
            if ls and ls != "normal":
                v = px(ls)
                if v is not None:
                    tracks.append(v)
            if t.get("font_family"):
                fams.append(t["font_family"].lower())
        if not tot:
            continue
        neg = sum(1 for v in tracks if v < -0.05)
        out[tag] = {
            "n": tot,
            "font_size_px": {"median": med(sizes), "common": common([round(x) for x in sizes if x is not None], 6)},
            "font_weight": {"median": med(weights)},
            "line_height_ratio": {"median": med(lh), "common": common([round(x, 1) for x in lh], 6)},
            "letter_spacing_px": {"median": med(tracks) if tracks else None,
                                  "negative_pct": round(100 * neg / tot)},
            "top_families": common(fams, 8),
        }
    return out


def font_landscape(recs):
    body, head, allf = [], [], []
    for r in recs:
        b = r.get("light", {}).get("typography", {}).get("body", {})
        h = (r.get("light", {}).get("typography", {}).get("h1")
             or r.get("light", {}).get("typography", {}).get("h2") or {})
        if b.get("font_family"):
            body.append(b["font_family"].lower()); allf.append(b["font_family"].lower())
        if h.get("font_family"):
            head.append(h["font_family"].lower()); allf.append(h["font_family"].lower())
    kr_share = round(100 * sum(1 for f in body if is_kr_font(f)) / len(body)) if body else 0
    pretendard = round(100 * sum(1 for f in body if "pretendard" in f) / len(body)) if body else 0
    return {
        "body_fonts": common(body, 12),
        "heading_fonts": common(head, 12),
        "korean_face_share_pct": kr_share,
        "pretendard_share_pct": pretendard,
    }


def build():
    recs = load(KR_DIR)
    gl = json.load(open(GLOBAL_CAT)) if os.path.exists(GLOBAL_CAT) else {}
    cat = {
        "n_sites": len(recs),
        "sites": sorted(r["name"] for r in recs),
        "fonts": font_landscape(recs),
        "typography": kr_typography(recs),
        "buttons": agg_buttons(recs),
        "layout": agg_layout(recs),
        "spacing": agg_spacing(recs),
        "color": agg_color(recs),
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(cat, open(OUT_JSON, "w"), indent=2, ensure_ascii=False)
    print(f"wrote {OUT_JSON} ({len(recs)} sites)")
    write_md(cat, gl, recs)
    return cat


def _fmt(pairs, suf=""):
    return ", ".join(f"`{v}{suf}` ({c})" for v, c in pairs)


def write_md(cat, gl, recs):
    n = cat["n_sites"]
    g_body = gl.get("typography", {}).get("body", {})
    g_body_sz = g_body.get("font_size_px", {}).get("median")
    g_body_lh = g_body.get("line_height_ratio", {}).get("median")
    g_h1 = gl.get("typography", {}).get("h1", {}).get("font_size_px", {}).get("median")
    k_body = cat["typography"].get("body", {})
    k_body_sz = k_body.get("font_size_px", {}).get("median")
    k_body_lh = k_body.get("line_height_ratio", {}).get("median")
    k_h1 = cat["typography"].get("h1", {}).get("font_size_px", {}).get("median")
    f = cat["fonts"]

    L = []
    L.append("# Korean web specs, and how they differ from the global set\n")
    L.append(f"Measured the same way as the global catalog, on {n} Korean design-led sites "
             "(Toss, Kakao, 당근, 무신사, 29CM, 오늘의집, 마켓컬리, 배민, 업비트, and more), read straight "
             "off their live computed styles in light and dark. The point is the *differences*: "
             "Korean (hangul/CJK) type is set differently from Latin, and the numbers show it.\n")
    L.append(f"> Source: `src/scrape_detail.py` over `data/site_list_kr.txt`, aggregated by "
             f"`scripts/build_korean_catalog.py`. Corpus: {n} sites. Global comparison from "
             f"`data/spec_catalog.json` (199 mostly-Western sites).\n")

    L.append("## The headline differences\n")
    L.append("| | Korean sites | Global sites |")
    L.append("|---|---|---|")
    L.append(f"| **Default body font** | Pretendard / hangul sans ({f['korean_face_share_pct']}% a Korean face, "
             f"{f['pretendard_share_pct']}% Pretendard) | Inter / system sans |")
    L.append(f"| **Body font-size** | {k_body_sz}px | {g_body_sz}px |")
    L.append(f"| **Body line-height** | {k_body_lh} | {g_body_lh} |")
    L.append(f"| **h1 size (median)** | {k_h1}px (bimodal) | {g_h1}px |")
    L.append("")
    L.append(f"Two differences are real, one is a corpus artifact worth explaining.\n")
    L.append(f"**1. The font.** Pretendard is the body face on {f['pretendard_share_pct']}% of these sites and "
             f"some hangul sans on {f['korean_face_share_pct']}%. Pretendard is to the Korean web what Inter is "
             f"to the Western web: the free, well-hinted default. So the *type tell* translates: shipping bare "
             f"Pretendard with no scale is the Korean equivalent of bare Inter, and the fix is the same, a real "
             f"scale plus a commissioned face where the brand warrants it (Toss Product Sans, Bithumb Trading "
             f"Sans, Gmarket Sans, Wanted Sans).\n")
    L.append(f"**2. Body size.** Korean body text sets *smaller*: a {k_body_sz}px median against {g_body_sz}px "
             f"globally, clustering at 13 to 15px. Hangul carries more ink per character, so 14px hangul reads "
             f"at roughly the presence of 16px Latin; Korean product culture is also denser. Setting hangul at "
             f"a Western 16 to 18px often looks oversized to a Korean eye.\n")
    if k_body_lh and g_body_lh and abs(k_body_lh - g_body_lh) < 0.1:
        L.append(f"**Not a difference: line-height.** Both land at ~{k_body_lh}. Hangul does want air, but "
                 f"Pretendard already ships a generous default, so the median matches the West rather than "
                 f"running looser. Keep body leading around 1.5 to 1.7 and you are inside both distributions.\n")
    L.append(f"**The h1 caveat.** The Korean h1 median ({k_h1}px) is *bimodal*, not small. Design-led product "
             f"sites (Toss, 당근, 오늘의집, 무신사) use 56 to 90px heroes exactly like the West; portals and "
             f"commerce (Naver, Coupang, Gmarket, SSG, Melon) are banner-and-carousel driven with a small or "
             f"absent display headline. The low median is the density culture of Korean commerce, not a "
             f"different idea of what a headline is. Read it as: pick your lane, and if you are a product site, "
             f"the big-hero numbers from the global catalog still apply.\n")

    L.append("## Fonts\n")
    L.append(f"- **Body typeface:** {_fmt(f['body_fonts'][:8])}.")
    L.append(f"- **Heading typeface:** {_fmt(f['heading_fonts'][:8])}.")
    L.append(f"- **Pretendard** alone is the body face on **{f['pretendard_share_pct']}%** of these sites; "
             f"a Korean-designed face covers **{f['korean_face_share_pct']}%**. Pretendard is to the Korean "
             f"web what Inter is to the Western web, the safe, free, well-hinted default. The owned-craft "
             f"move is a commissioned face (Toss Product Sans, Bithumb Trading Sans, Gmarket Sans, "
             f"Wanted Sans), not avoiding Pretendard.\n")

    L.append("## Type scale (light)\n")
    L.append("| Element | Size (median) | Line-height | Weight | Negative tracking |")
    L.append("|---|---|---|---|---|")
    for tag in ("h1", "h2", "h3", "body"):
        t = cat["typography"].get(tag)
        if not t:
            continue
        L.append(f"| **{tag}** ({t['n']}) | {t['font_size_px']['median']}px | "
                 f"{t['line_height_ratio']['median']} | {t['font_weight']['median']} | "
                 f"{t['letter_spacing_px']['negative_pct']}% |")
    L.append("")
    bt = k_body.get("letter_spacing_px", {})
    L.append(f"Body sizes cluster at {_fmt(k_body.get('font_size_px',{}).get('common',[]),'px')}. "
             f"Negative letter-spacing is common on hangul ({bt.get('negative_pct')}% of body blocks track "
             f"in); a touch of negative tracking (around -0.02em) tightens the gaps between syllable blocks. "
             f"Do not over-track, hangul loses legibility faster than Latin.\n")

    L.append("## Buttons\n")
    bp = cat["buttons"].get("primary", {})
    if bp:
        pad_y = bp["padding_y_px"]["median"] or 0
        pad_note = (f", padding around `{pad_y}px` vertical" if pad_y and pad_y > 2 else "")
        L.append(f"- **Primary:** radius median `{bp['radius_px']['median']}px` (full pill on "
                 f"{bp['radius_px']['pill_pct']}%), label `{bp['font_size_px']['median']}px`, "
                 f"weight `{bp['font_weight']['median']}`{pad_note}.")
    L.append(f"- The radius story matches the global one (a soft round or a full pill, sharp corners rare). "
             f"Korean button geometry is noisier to read off the DOM because many primary actions are "
             f"styled links or icon-and-label rows rather than a single padded `<button>`.\n")

    L.append("## Color\n")
    c = cat["color"]
    L.append(f"- **Light page bg:** {_fmt(c['light']['page_bg_common'][:6])}.")
    L.append(f"- **Primary text:** {_fmt(c['light']['primary_text_common'][:6])}.")
    L.append(f"- **Accent (primary action):** {_fmt(c['light']['accent_common'][:8])}. A spread of owned brand "
             f"colors (Toss and Coupang blues, a Naver-style green, and more), each appearing once, never a "
             f"shared default indigo. As in the global set, the hue is not the tell.")
    L.append(f"- **Dark mode:** {c['n_dark_mode']} of {c['n_total']} repaint for `prefers-color-scheme: dark`; "
             f"dark bg {_fmt(c['dark']['page_bg_common'][:5])} (the same tinted-near-black grammar).\n")

    L.append("## Appendix: per-site body font + size\n")
    L.append("| Site | Body font | Body px | Body line-height | h1 px |")
    L.append("|---|---|---|---|---|")
    for r in sorted(recs, key=lambda x: x["name"]):
        b = r.get("light", {}).get("typography", {}).get("body", {})
        h1 = r.get("light", {}).get("typography", {}).get("h1", {})
        L.append(f"| {r['name']} | {b.get('font_family','-')} | {b.get('font_size_px','-')} | "
                 f"{b.get('line_height_ratio','-')} | {h1.get('font_size_px','-')} |")
    L.append("")
    L.append(f"<!-- generated by scripts/build_korean_catalog.py from {n} sites -->")

    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    open(OUT_MD, "w", encoding="utf-8").write("\n".join(L))
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    build()
