"""Compatibility shim for `python mcp/server.py`. The MCP server now lives in
`ai_design_tells.server` and installs as the `ai-design-tells-mcp` command.
Prefer registering via uvx (see README). ROOT is appended (not inserted) so the
installed `mcp` SDK keeps precedence over this repo's `mcp/` directory.
"""
import os as _os
import sys as _sys

_sys.path.append(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from ai_design_tells.server import mcp, main     # noqa: F401,E402

if __name__ == "__main__":
    main()
