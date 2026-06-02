"""
ai_design_tells, a measurable taxonomy of the AI-generated design look.

The "AI look" is a finite, enumerable set of statistical defaults, so it is
measurable. This package is the taxonomy (27 tells across 8 families), a
dependency-free static detector (the Tell Score, 0-100, lower is better), a CLI,
and an MCP server so any coding agent can audit the UI it just wrote.

Public API:
    from ai_design_tells import score_document, TELLS, FAMILIES
    rep = score_document(open("page.html").read())
    print(rep.score, rep.grade)

CLI:        ai-design-tells page.html
MCP server: ai-design-tells-mcp   (register with uvx, see README)
"""
from .taxonomy import TELLS, FAMILIES, max_score, tells_by_family
from .scorer import score_document, Report, TellResult

__all__ = [
    "score_document", "Report", "TellResult",
    "TELLS", "FAMILIES", "max_score", "tells_by_family",
]

__version__ = "0.4.0"
