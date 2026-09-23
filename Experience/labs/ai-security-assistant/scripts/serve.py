"""Start the API server with both of the project's source roots on `sys.path`.

The FastAPI app lives in `backend/app`, while the domain packages (`llm`,
`security`, `agent`, `rag`, ...) live in the repository root. A bare
`uvicorn app.main:app --app-dir backend` puts only `backend/` on the import
path, so it dies with `ModuleNotFoundError: No module named 'llm'` — uvicorn's
console script never adds the working directory, unlike `python -m uvicorn`.

This runner makes BOTH roots importable, moves into the project root (so
`Settings` always finds `.env`, which is loaded relative to the CWD) and then
hands over to uvicorn.

Run:  python scripts/serve.py                  # http://127.0.0.1:8000
      APP_PORT=9000 python scripts/serve.py
      APP_RELOAD=1 python scripts/serve.py     # auto-reload on edits

Equivalent without this script (run it from the project root):
      PYTHONPATH=.:backend uvicorn app.main:app --app-dir backend --port 8000
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

for _path in (str(PROJECT_ROOT), str(BACKEND_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# uvicorn's reload mode starts a fresh (spawned) process: PYTHONPATH is the
# reliable way to carry both roots over to it.
_existing = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = os.pathsep.join(
    entry for entry in (str(PROJECT_ROOT), str(BACKEND_DIR), _existing) if entry
)

# `.env` is loaded relative to the working directory → always start from the root.
os.chdir(PROJECT_ROOT)


def main() -> None:
    """Run uvicorn against `app.main:app` with local-development defaults."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", "8000")),
        reload=os.getenv("APP_RELOAD", "").lower() in {"1", "true", "yes"},
        app_dir=str(BACKEND_DIR),
    )


if __name__ == "__main__":
    main()
