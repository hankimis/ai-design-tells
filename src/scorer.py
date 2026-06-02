"""Compatibility shim. The detector now lives in `ai_design_tells.scorer`.
Edit `ai_design_tells/scorer.py`, not this file.
"""
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from ai_design_tells.scorer import *             # noqa: F401,F403,E402
from ai_design_tells.scorer import (             # noqa: F401,E402
    score_document, score_signals, Document, Report, TellResult, craft_credits,
)
