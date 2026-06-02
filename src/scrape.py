"""Compatibility shim. The live scraper now lives in `ai_design_tells.scrape`.
Edit `ai_design_tells/scrape.py`, not this file.
"""
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from ai_design_tells.scrape import *             # noqa: F401,F403,E402
