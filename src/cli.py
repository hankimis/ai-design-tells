#!/usr/bin/env python3
"""
aidt — the AI Design Tells linter CLI.

Usage:
  python src/cli.py path/to/page.html            # score one file
  python src/cli.py fixtures/*.html              # score many, table
  python src/cli.py page.html --json             # machine-readable
  python src/cli.py page.html --verbose          # show every tell + fix

Exit code is the integer TELL SCORE (0-100, lower is better), so it can gate CI:
  aidt build/index.html || echo "too many AI tells"
"""
import sys
import os
import glob
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scorer import score_document  # noqa: E402
from taxonomy import FAMILIES       # noqa: E402

C = {"red": "\033[31m", "grn": "\033[32m", "yel": "\033[33m",
     "dim": "\033[2m", "bold": "\033[1m", "cyan": "\033[36m", "rst": "\033[0m"}
if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
    C = {k: "" for k in C}


def colorize(score):
    if score < 28:
        return C["grn"]
    if score < 45:
        return C["yel"]
    return C["red"]


def render(path, rep, verbose):
    bar_len = 40
    filled = int(round(rep.score / 100 * bar_len))
    bar = "█" * filled + "░" * (bar_len - filled)
    col = colorize(rep.score)
    print(f"\n{C['bold']}{path}{C['rst']}")
    print(f"  {col}{bar}{C['rst']}  {col}{C['bold']}{rep.score:5.1f}{C['rst']}/100   {rep.grade}")
    print(f"  {C['dim']}fired {rep.fired_weight:.0f} of {rep.max_weight:.0f} tell-weight (lower is better){C['rst']}")
    # family breakdown
    print(f"  {C['dim']}by family:{C['rst']}", end=" ")
    for k, (name, _) in FAMILIES.items():
        fs = rep.family_scores[k]
        cc = colorize(fs)
        print(f"{cc}{k}:{fs:3.0f}{C['rst']}", end="  ")
    print()
    fired = [r for r in rep.results if r.fired]
    if fired:
        print(f"  {C['bold']}tells fired:{C['rst']}")
        for r in sorted(fired, key=lambda x: -x.weight):
            tag = "TELL " if r.severity == "tell" else "smell"
            print(f"    {col}●{C['rst']} [{r.id}] {r.name} {C['dim']}(+{r.weight:g}, {tag}){C['rst']}")
            for e in r.evidence:
                print(f"        {C['dim']}↳ {e}{C['rst']}")
            if verbose:
                print(f"        {C['cyan']}fix:{C['rst']} {r.fix}")
    else:
        print(f"  {C['grn']}no tells fired — reads as intentional.{C['rst']}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    paths = []
    for a in args:
        paths += glob.glob(a) if any(ch in a for ch in "*?[") else [a]
    if not paths:
        print(__doc__)
        sys.exit(2)

    reports = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            rep = score_document(f.read())
        reports.append((p, rep))

    if "--json" in flags:
        out = {p: {
            "score": round(rep.score, 2),
            "grade": rep.grade,
            "fired_weight": rep.fired_weight,
            "max_weight": rep.max_weight,
            "family_scores": {k: round(v, 1) for k, v in rep.family_scores.items()},
            "tells": [{"id": r.id, "name": r.name, "family": r.family,
                       "weight": r.weight, "severity": r.severity,
                       "fired": r.fired, "evidence": r.evidence, "fix": r.fix}
                      for r in rep.results],
        } for p, rep in reports}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        sys.exit(int(round(reports[0][1].score)))

    if "--quiet" in flags or "-q" in flags:
        print(f"\n  {C['bold']}AI Design Tells — leaderboard{C['rst']}  {C['dim']}(Tell Score, lower is better){C['rst']}\n")
        for p, rep in sorted(reports, key=lambda x: x[1].score):
            col = colorize(rep.score)
            bar_len = 28
            filled = int(round(rep.score / 100 * bar_len))
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"   {col}{bar}{C['rst']}  {col}{C['bold']}{rep.score:5.1f}{C['rst']}  "
                  f"{os.path.basename(p):24} {C['dim']}{rep.grade}{C['rst']}")
        print()
        sys.exit(int(round(reports[0][1].score)))

    for p, rep in reports:
        render(p, rep, "--verbose" in flags or "-v" in flags)

    if len(reports) > 1:
        print(f"\n{C['bold']}summary{C['rst']} (lower is better)")
        for p, rep in sorted(reports, key=lambda x: x[1].score):
            col = colorize(rep.score)
            print(f"  {col}{rep.score:5.1f}{C['rst']}  {os.path.basename(p)}")
    print()
    sys.exit(int(round(reports[0][1].score)))


if __name__ == "__main__":
    main()
