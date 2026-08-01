# -*- coding: utf-8 -*-
"""pytest bootstrap for the eval gate.

Two jobs, both small:

  1. Load `.env` the same way every `labs/lab_*.py` does, so `pytest tests/`
     picks up the key you already configured for the labs. `setdefault` means a
     real environment variable (or a CI secret) always wins over the file.

  2. Make the repo importable when the labs were NOT pip-installed, so a student
     who just cloned can run the gate immediately.

Nothing here touches your key beyond putting it in `os.environ` — it is never
printed, logged, or written anywhere.
"""
from __future__ import annotations

import os
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Editable installs already put mai_rag on the path; this is the fallback for a
# bare `git clone` with no `pip install -e .`.
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# MAI_NO_DOTENV=1 ignores the local .env — that's how you prove the keyless CI
# path really is green before you trust it. (CI itself has no .env at all.)
if not os.getenv("MAI_NO_DOTENV"):
    _envfile = _ROOT / ".env"
    if _envfile.exists():
        for _line in _envfile.read_text(encoding="utf-8").splitlines():
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
