#!/usr/bin/env python3
"""Score every fixture and write results/scores.json (the data behind the figures)."""
import sys, os, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from scorer import score_document          # noqa: E402
from taxonomy import TELLS, FAMILIES, max_score  # noqa: E402

ROOT = os.path.join(HERE, "..")
CORPUS = {
    # name: (path, family_label)
    "ai-default":       ("fixtures/ai-default.html",      "AI-default"),
    "slop-pricing":     ("fixtures/slop-pricing.html",    "AI-default"),
    "slop-dashboard":   ("fixtures/slop-dashboard.html",  "AI-default"),
    "refined":          ("fixtures/refined.html",         "Designed"),
    "designed-docs":    ("fixtures/designed-docs.html",   "Designed"),
    "designed-pricing": ("fixtures/designed-pricing.html","Designed"),
}

def main():
    out = {"max_weight": max_score(), "families": {k: v[0] for k, v in FAMILIES.items()},
           "tells": [{"id": t.id, "nickname": t.nickname, "family": t.family, "name": t.name,
                      "weight": t.weight, "severity": t.severity} for t in TELLS],
           "pages": {}}
    for name, (rel, label) in CORPUS.items():
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            rep = score_document(f.read())
        out["pages"][name] = {
            "label": label, "path": rel, "score": round(rep.score, 2), "grade": rep.grade,
            "family_scores": {k: round(v, 2) for k, v in rep.family_scores.items()},
            "fired": {r.id: r.fired for r in rep.results},
        }
        print(f"{rep.score:6.1f}  [{label:10}] {name}")
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "scores.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nwrote results/scores.json")

if __name__ == "__main__":
    main()
