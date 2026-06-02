#!/usr/bin/env python3
"""
AI Design Tells, MCP server.

Exposes the Tell Score detector to any MCP client (Claude Code, Claude Desktop,
Cursor, …) so an agent can audit the UI it just wrote *before* shipping it, and
get back the specific fixes. Pure-stdlib detector; the only dependency is the
MCP SDK itself.

Tools
  score_design(html)      score an HTML string; returns score, grade, fired tells + fixes
  score_file(path)        read a local .html file and score it
  audit_url(url)          render a live URL in headless Chrome and score its computed styles
  list_tells()            the full taxonomy (id, family, weight, why, fix)
  component_specs()       concrete CSS target values measured from 199 real sites
  korean_specs()          CSS targets for the Korean (hangul) web + KR-vs-global diffs
  harness_prompt()        a ready-to-paste system-prompt section that pre-empts the tells

Run (stdio):  ai-design-tells-mcp        (after `pip install ai-design-tells`)
Register in Claude Code (.mcp.json), zero-clone via uvx:
  { "mcpServers": { "ai-design-tells": {
      "command": "uvx", "args": ["--from", "ai-design-tells", "ai-design-tells-mcp"] } } }
"""
import os

from .scorer import score_document          # noqa: E402
from .taxonomy import TELLS, FAMILIES        # noqa: E402

from mcp.server.fastmcp import FastMCP       # noqa: E402

_PKG = os.path.dirname(os.path.abspath(__file__))

mcp = FastMCP("ai-design-tells")


def _data_path(*parts):
    """Locate a bundled asset. Prefer the repo's freshly-generated copy in dev
    (ai_design_tells/../<parts>), fall back to the copy bundled in the installed
    package (ai_design_tells/<parts>)."""
    repo = os.path.join(_PKG, "..", *parts)
    if os.path.exists(repo):
        return repo
    return os.path.join(_PKG, *parts)


def _report_dict(html: str) -> dict:
    rep = score_document(html)
    fired = [
        {"id": r.id, "nickname": r.nickname, "family": FAMILIES[r.family][0], "name": r.name,
         "weight": r.weight, "severity": r.severity, "evidence": r.evidence, "fix": r.fix}
        for r in rep.results if r.fired
    ]
    fired.sort(key=lambda x: -x["weight"])
    return {
        "tell_score": round(rep.score, 1),
        "grade": rep.grade,
        "lower_is_better": True,
        "family_scores": {FAMILIES[k][0]: round(v, 1) for k, v in rep.family_scores.items()},
        "fired_tells": fired,
        "summary": (f"Tell Score {rep.score:.0f}/100 ({rep.grade}). "
                    f"{len(fired)} tell(s) fired. Apply the listed fixes to lower it."),
    }


@mcp.tool()
def score_design(html: str) -> dict:
    """Score an HTML/CSS UI string for AI design tells.

    Returns the Tell Score (0-100, lower is better, 0 reads as human-crafted,
    high reads as AI slop), a letter grade, per-family scores, and every tell
    that fired with concrete evidence and the specific fix to apply. Use this to
    audit a page you just generated before showing it to the user."""
    return _report_dict(html)


@mcp.tool()
def score_file(path: str) -> dict:
    """Score a local .html file for AI design tells. Same output as score_design."""
    if not os.path.exists(path):
        return {"error": f"file not found: {path}"}
    with open(path, encoding="utf-8") as f:
        out = _report_dict(f.read())
    out["path"] = path
    return out


@mcp.tool()
def audit_url(url: str) -> dict:
    """Audit a LIVE website for AI design tells. Renders the page in headless
    Chrome, reads its computed styles, and scores them with the detector that was
    recalibrated on 202 real top-tier sites, so genuine craft (a brand purple, a
    custom font with optical tracking) is not mistaken for AI. Returns the Tell
    Score, the craft credits that offset cosmetic defaults, and the fired tells.
    Needs the Playwright extra (pip install -r requirements.txt). Use this to
    audit a real deployed site, not a code string (use score_design for code)."""
    import tempfile
    try:
        from .scrape import scrape
        from .scorer import score_signals
    except Exception as e:
        return {"error": f"live audit needs the Playwright extra: {e}"}
    out = tempfile.mkdtemp(prefix="aidt_")
    recs = scrape([url], out, resume=False)
    rec = next(iter(recs.values()))
    if not rec.get("ok"):
        return {"error": f"could not load {url}: {rec.get('error','')}"}
    rep = score_signals(rec)
    fired = [{"id": r.id, "nickname": r.nickname, "family": FAMILIES[r.family][0], "name": r.name,
              "weight": r.weight, "severity": r.severity, "evidence": r.evidence}
             for r in rep.results if r.fired]
    fired.sort(key=lambda x: -x["weight"])
    return {
        "url": url, "tell_score": round(rep.score, 1), "grade": rep.grade,
        "lower_is_better": True,
        "craft_credits": getattr(rep, "credit_list", []),
        "family_scores": {FAMILIES[k][0]: round(v, 1) for k, v in rep.family_scores.items()},
        "fired_tells": fired,
        "summary": (f"Tell Score {rep.score:.0f}/100 ({rep.grade}). "
                    f"{len(fired)} tell(s) fired; craft credits offsetting cosmetic defaults: "
                    f"{', '.join(getattr(rep,'credit_list',[])) or 'none'}."),
    }


@mcp.tool()
def list_tells() -> list:
    """Return the full AI Design Tells taxonomy: id, family, weight, severity,
    why it reads as a machine default, and the intentional fix."""
    return [
        {"id": t.id, "nickname": t.nickname, "family": FAMILIES[t.family][0], "name": t.name,
         "weight": t.weight, "severity": t.severity, "why": t.why, "fix": t.fix}
        for t in TELLS
    ]


@mcp.tool()
def component_specs() -> dict:
    """Return measured, concrete CSS target values from a catalog of 199 real
    design-led sites: button radius/padding/weight, the type scale (h1-body sizes,
    line-heights, tracking), layout container widths and section rhythm, the 4/8px
    spacing scale, and light + dark color palettes (page bg, text, accents,
    surfaces). Use this when building UI to pick values that match what top sites
    ship, instead of framework defaults. Companion to the negative `list_tells`."""
    path = _data_path("data", "spec_catalog.json")
    if not os.path.exists(path):
        return {"error": "catalog not built; run scripts/build_spec_catalog.py"}
    import json
    return json.load(open(path, encoding="utf-8"))


@mcp.tool()
def korean_specs() -> dict:
    """Return measured CSS targets for the KOREAN (hangul/CJK) web, from a catalog of
    48 Korean design-led sites (Toss, Kakao, 당근, 무신사, 29CM, 오늘의집, 배민, 업비트...),
    plus how they differ from the global set. Key differences: Pretendard is the default
    body face (not Inter), body text sets smaller (~14px vs 16px), while line-height is
    about the same (~1.5). Use this when building UI for a Korean audience. Companion to
    `component_specs`."""
    path = _data_path("data", "korean_catalog.json")
    if not os.path.exists(path):
        return {"error": "Korean catalog not built; run scripts/build_korean_catalog.py"}
    import json
    return json.load(open(path, encoding="utf-8"))


@mcp.tool()
def harness_prompt() -> str:
    """Return a ready-to-paste system-prompt / CLAUDE.md section that instructs a
    coding agent to avoid every tell up front (prevention, not just detection)."""
    path = _data_path("harness", "AI-DESIGN-TELLS.md")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    # fallback: synthesize from the taxonomy
    lines = ["# Avoid these AI design tells\n"]
    for t in TELLS:
        lines.append(f"- **{t.name}**, {t.why}. Instead: {t.fix}.")
    return "\n".join(lines)


def main():
    """Console-script entry point: run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
