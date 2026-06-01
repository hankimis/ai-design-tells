"""Validate the recalibrated live detector against the real-site corpus.

A good discriminator must score human-crafted top sites LOW (else it just flags
everything). This prints the score distribution over the corpus and the highest
scorers (candidate false positives to inspect), and writes data/site_scores.json.
"""
import os, sys, json, glob, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from scorer import score_signals, _load_calib  # noqa: E402

def main():
    calib = _load_calib()
    rows = []
    for fp in sorted(glob.glob(os.path.join(ROOT, "data", "sites", "*.json"))):
        d = json.load(open(fp, encoding="utf-8"))
        if not d.get("ok"):
            continue
        rep = score_signals(d, calib)
        fired = [r.id for r in rep.results if r.fired]
        rows.append({"name": d["name"], "url": d["url"], "score": round(rep.score, 1),
                     "grade": rep.grade, "credits": rep.credits,
                     "credit_list": rep.credit_list, "fired": fired})
    scores = [r["score"] for r in rows]
    print(f"corpus: {len(rows)} human-crafted sites")
    print(f"  Tell Score  median={st.median(scores):.1f}  mean={st.mean(scores):.1f}  "
          f"p90={sorted(scores)[int(len(scores)*0.9)]:.1f}  max={max(scores):.1f}")
    grades = {}
    for r in rows:
        g = r["grade"].split(",")[0].strip()
        grades[g] = grades.get(g, 0) + 1
    print("  grade mix:", grades)
    print("\nHighest-scoring real sites (inspect for false positives):")
    for r in sorted(rows, key=lambda x: -x["score"])[:14]:
        print(f"  {r['score']:5.1f}  {r['name']:26} credits={r['credits']} "
              f"fired={','.join(r['fired'])}")
    print("\nLowest (cleanest) real sites:")
    for r in sorted(rows, key=lambda x: x["score"])[:6]:
        print(f"  {r['score']:5.1f}  {r['name']:26} fired={','.join(r['fired']) or 'none'}")
    json.dump(rows, open(os.path.join(ROOT, "data", "site_scores.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("\nwrote data/site_scores.json")

if __name__ == "__main__":
    main()
