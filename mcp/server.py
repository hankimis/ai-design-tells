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
  list_tells()            the full taxonomy (id, family, weight, why, fix)
  harness_prompt()        a ready-to-paste system-prompt section that pre-empts the tells

Run (stdio):  python mcp/server.py
Register in Claude Code (.mcp.json):
  { "mcpServers": { "ai-design-tells": {
      "command": "python", "args": ["mcp/server.py"] } } }
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from scorer import score_document          # noqa: E402
from taxonomy import TELLS, FAMILIES        # noqa: E402

from mcp.server.fastmcp import FastMCP       # noqa: E402

mcp = FastMCP("ai-design-tells")


def _report_dict(html: str) -> dict:
    rep = score_document(html)
    fired = [
        {"id": r.id, "family": FAMILIES[r.family][0], "name": r.name,
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
def list_tells() -> list:
    """Return the full AI Design Tells taxonomy: id, family, weight, severity,
    why it reads as a machine default, and the intentional fix."""
    return [
        {"id": t.id, "family": FAMILIES[t.family][0], "name": t.name,
         "weight": t.weight, "severity": t.severity, "why": t.why, "fix": t.fix}
        for t in TELLS
    ]


@mcp.tool()
def harness_prompt() -> str:
    """Return a ready-to-paste system-prompt / CLAUDE.md section that instructs a
    coding agent to avoid every tell up front (prevention, not just detection)."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "..", "harness", "AI-DESIGN-TELLS.md")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    # fallback: synthesize from the taxonomy
    lines = ["# Avoid these AI design tells\n"]
    for t in TELLS:
        lines.append(f"- **{t.name}**, {t.why}. Instead: {t.fix}.")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
