"""
analyze_corpus.py, learn the empirical distribution of human-crafted design from
the scraped real-site corpus, and write data/calibration.json that the recalibrated
detector reads. This is the "learning" step: thresholds come from where real
top-tier sites actually sit, not from a hand-guess.

Key lessons the data forces (see paper §Recalibration):
  - Purple hue is NOT a tell (Stripe owns #635bff): only the *exact default indigo*
    ramp discriminates. Generic purple becomes a weak, co-occurrence-gated smell.
  - Inter is NOT a tell (Linear ships it with a real type system): the tell is a
    generic font WITH no compensating craft (no negative tracking, no scale).
  - 10-15 distinct font sizes is NORMAL for a rich site, not "no scale": drop the
    high-count branch; keep only the degenerate 1-2-size case.
  - focus-visible read from cssRules is a false-negative when stylesheets are
    cross-origin (Stripe: 0 readable sheets). Confidence-gate it.
  - Real sites use 5+ distinct radii (a hierarchy); one radius everywhere is the tell.
"""
import os, sys, json, glob, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SITES = os.path.join(ROOT, "data", "sites")

GENERIC_FONTS = {"inter", "inter variable", "roboto", "arial", "helvetica", "helvetica neue",
                 "system-ui", "-apple-system", "segoe ui", "sans-serif", "open sans", "lato"}
# The exact AI-default indigo ramp (Tailwind/shadcn). Brand purples (Stripe #635bff) are NOT here.
DEFAULT_INDIGO = {"#6366f1", "#4f46e5", "#4338ca", "#818cf8", "#a5b4fc", "#6d28d9", "#7c3aed"}


def pct(xs, p):
    if not xs:
        return 0
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100
    f = int(k)
    return xs[f] if f + 1 >= len(xs) else xs[f] + (xs[f+1]-xs[f]) * (k - f)


def main():
    sites = []
    for fp in sorted(glob.glob(os.path.join(SITES, "*.json"))):
        d = json.load(open(fp, encoding="utf-8"))
        if d.get("ok"):
            sites.append(d)
    n = len(sites)
    print(f"loaded {n} OK sites\n")

    # ---- distributions ----
    radius_counts = [len(d["radii"]) for d in sites]
    fontsize_counts = [len(d["font_sizes"]) for d in sites]
    centered = [d["layout"]["centered_fraction"] for d in sites]
    purple_acc = [d["color"]["purple_accents"] for d in sites]
    bp_grad = [d["color"]["blue_purple_gradients"] for d in sites]
    emoji = [d["emoji_headings"] for d in sites]
    # font genericness
    generic_body = sum(1 for d in sites if d["fonts"]["body"] in GENERIC_FONTS)
    # negative tracking adoption among sites that have big headings
    trk = [d["heading"]["neg_tracked"]/max(1, d["heading"]["big_count"]) for d in sites if d["heading"]["big_count"]]
    # focus reliability: only sites with readable same-origin sheets
    reliable_focus = [d for d in sites if d["focus"]["sheets_read"] >= 3]
    focus_yes = sum(1 for d in reliable_focus if d["focus"]["focus_visible"])
    # exact-default-indigo prevalence (recompute from accent hues is lossy; we only
    # stored hues, so report purple-accent prevalence as the *brand* purple signal)
    any_purple = sum(1 for d in sites if d["color"]["purple_accents"] > 0)

    def line(label, xs):
        print(f"  {label:26} min={min(xs):5.2f} p10={pct(xs,10):5.2f} median={st.median(xs):5.2f} "
              f"p90={pct(xs,90):5.2f} max={max(xs):5.2f}")

    print("EMPIRICAL DISTRIBUTIONS (human-crafted top-tier sites)")
    line("distinct radii / site", radius_counts)
    line("distinct font sizes / site", fontsize_counts)
    line("centered block fraction", centered)
    line("purple accents / site", purple_acc)
    line("blue-purple gradients", bp_grad)
    line("emoji headings", emoji)
    print(f"\n  generic primary font:      {generic_body}/{n} sites ({100*generic_body/n:.0f}%)  "
          f"(Inter/system; NOT a tell on its own)")
    print(f"  brand purple present:      {any_purple}/{n} sites ({100*any_purple/n:.0f}%)  "
          f"(purple hue is common in good design)")
    print(f"  neg-tracked display type:  median {st.median(trk)*100:.0f}% of big headings")
    print(f"  focus-visible (readable):  {focus_yes}/{len(reliable_focus)} sites with same-origin CSS")

    # ---- chosen calibration (thresholds anchored to the real distribution) ----
    calib = {
        "_note": "Learned from the real-site corpus. Thresholds sit at the edge of where "
                 "human-crafted sites live, so top sites score near zero and only the "
                 "default bundle scores high.",
        "n_sites": n,
        "default_indigo_hexes": sorted(DEFAULT_INDIGO),
        "generic_fonts": sorted(GENERIC_FONTS),
        # one-radius tell: fire only well below the human p10 of distinct radii
        "radius_distinct_min": max(2, int(pct(radius_counts, 10))),
        # font-size "no scale" tell: only the degenerate low end; high counts are normal
        "fontsize_low_max": 3,
        "fontsize_high_min": int(pct(fontsize_counts, 95)) + 6,   # effectively off unless extreme
        # center-everything: human p90 is the ceiling of normal
        "centered_fraction_min": round(max(0.5, pct(centered, 95) + 0.25), 2),
        # purple: brand purple is fine; only the exact default indigo, or purple WITH the
        # default bundle, counts. generic purple-hue weight is set low and gated.
        "purple_exact_only": True,
        # focus tell only when we could actually read the CSS
        "focus_min_readable_sheets": 3,
        # craft credits: signals that, when present, offset cosmetic tells
        "craft_signals": {
            "custom_display_font": "primary font not in generic_fonts",
            "negative_tracking": "neg_tracked/big_count >= 0.5",
            "radius_hierarchy": f"distinct radii >= {max(3, int(pct(radius_counts,25)))}",
        },
        "radius_hierarchy_min": max(3, int(pct(radius_counts, 25))),
    }
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "calibration.json"), "w", encoding="utf-8") as f:
        json.dump(calib, f, ensure_ascii=False, indent=2)
    print("\nwrote data/calibration.json")
    print(json.dumps({k: v for k, v in calib.items() if not k.startswith("_") and k != "generic_fonts"
                      and k != "default_indigo_hexes"}, indent=2))


if __name__ == "__main__":
    main()
