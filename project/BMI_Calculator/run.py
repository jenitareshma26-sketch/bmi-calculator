#!/usr/bin/env python3
"""Bootstrap script for BMI Calculator.

Loads the _tkinter extension module from a non-standard path
when the system python3-tk package is not installed, then
launches the main application.
"""

import sys
import os
import importlib.util

# ── _tkinter bootstrap ─────────────────────────────────────────────────────

_TKINTER_SO = "/tmp/py3tk_extract/usr/lib/python3.13/lib-dynload/_tkinter.cpython-313-x86_64-linux-gnu.so"

if "_tkinter" not in sys.modules and os.path.exists(_TKINTER_SO):
    spec = importlib.util.spec_from_file_location("_tkinter", _TKINTER_SO)
    _tkinter_mod = importlib.util.module_from_spec(spec)
    sys.modules["_tkinter"] = _tkinter_mod
    spec.loader.exec_module(_tkinter_mod)

# ── Launch app ──────────────────────────────────────────────────────────────

sys.path.insert(0, os.path.dirname(__file__))
from main import main

if __name__ == "__main__":
    main()
