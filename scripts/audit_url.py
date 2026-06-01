#!/usr/bin/env python3
"""
audit_url.py, audit a LIVE site for AI design tells.

This is the v2 capability the static file detector could not do: it renders the
page in headless Chrome, reads the *computed styles* off the live DOM, and scores
them with the data-recalibrated detector (calibrated on 202 real top-tier sites,
so good craft is not mistaken for AI). Needs the extras: pip install -r requirements.txt

Usage:
  python scripts/audit_url.py https://your-site.com
  python scripts/audit_url.py https://a.com https://b.com   # several, ranked
"""
import os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
from scorer import score_signals, _load_calib  # noqa: E402

C = {"red": "\033[31m", "grn": "\033[32m", "yel": "\033[33m", "dim": "\033[2m",
     "bold": "\033[1m", "cyan": "\033[36m", "rst": "\033[0m"}
if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
    C = {k: "" for k in C}


def col(s):
    return C["grn"] if s < 28 else C["yel"] if s < 45 else C["red"]


def main():
    urls = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not urls:
        print(__doc__); sys.exit(2)
    from scrape import scrape
    calib = _load_calib()
    out = tempfile.mkdtemp(prefix="aidt_audit_")
    recs = scrape(urls, out, resume=False)
    results = []
    for name, rec in recs.items():
        if not rec.get("ok"):
            print(f"\n{C['bold']}{rec['url']}{C['rst']}  {C['red']}could not load{C['rst']} ({rec.get('error','')[:80]})")
            continue
        rep = score_signals(rec, calib)
        results.append((rec["url"], rep))
        c = col(rep.score)
        bar = "█" * int(round(rep.score/100*36)) + "░" * (36 - int(round(rep.score/100*36)))
        print(f"\n{C['bold']}{rec['url']}{C['rst']}")
        print(f"  {c}{bar}{C['rst']}  {c}{C['bold']}{rep.score:5.1f}{C['rst']}/100   {rep.grade}")
        if rep.credit_list:
            print(f"  {C['grn']}craft credits:{C['rst']} {', '.join(rep.credit_list)}")
        fired = [r for r in rep.results if r.fired]
        if fired:
            for r in sorted(fired, key=lambda x: -x.weight):
                print(f"    {c}●{C['rst']} [{r.id}] {r.name} {C['dim']}(+{r.weight:g}){C['rst']}")
                for e in r.evidence:
                    print(f"        {C['dim']}↳ {e}{C['rst']}")
        else:
            print(f"  {C['grn']}no tells fired, reads as human-crafted.{C['rst']}")
    if len(results) > 1:
        print(f"\n{C['bold']}ranked (lower is better){C['rst']}")
        for u, rep in sorted(results, key=lambda x: x[1].score):
            print(f"  {col(rep.score)}{rep.score:5.1f}{C['rst']}  {u}")
    print()
    if results:
        sys.exit(int(round(results[0][1].score)))


if __name__ == "__main__":
    main()
