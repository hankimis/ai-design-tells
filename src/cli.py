"""Compatibility shim for `python src/cli.py`. The CLI now lives in
`ai_design_tells.cli` and installs as the `ai-design-tells` command.
"""
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from ai_design_tells.cli import main             # noqa: E402

if __name__ == "__main__":
    main()
