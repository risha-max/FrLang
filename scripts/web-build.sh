#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="python"
if [[ -x .venv/bin/python ]]; then
  PYTHON=".venv/bin/python"
fi

(cd web && npm install && npm run build)
"$PYTHON" -m pip install -e ".[web]" -q
echo "Build web terminé. Lance : $PYTHON -m uvicorn frlang.web.app:app --host 0.0.0.0 --port 8000"
