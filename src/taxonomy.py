"""Compatibility shim. The taxonomy now lives in `ai_design_tells.taxonomy`,
the single source of truth. Kept so tooling that does
`sys.path.insert(0, "src"); from taxonomy import ...` keeps working.
Edit `ai_design_tells/taxonomy.py`, not this file.
"""
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from ai_design_tells.taxonomy import *          # noqa: F401,F403,E402
from ai_design_tells.taxonomy import (          # noqa: F401,E402
    Tell, TELLS, FAMILIES, max_score, tells_by_family,
    VAGUE_HEADLINE_RE, GENERIC_CTA,
)
