#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="python"
if [[ -x .venv/bin/python ]]; then
  PYTHON=".venv/bin/python"
fi

if [[ ! -d web/node_modules ]]; then
  echo "Installation des dépendances web…"
  (cd web && npm install)
fi

if ! "$PYTHON" -c "import fastapi, watchfiles" >/dev/null 2>&1; then
  echo "Installation des dépendances Python web…"
  "$PYTHON" -m pip install -e ".[web,lsp]" -q
fi

free_port() {
  local port="$1"
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" >/dev/null 2>&1 || true
  fi
}

cleanup() {
  jobs -p | xargs -r kill 2>/dev/null || true
}
trap cleanup EXIT

free_port 8765
free_port 8000
free_port 5173

"$PYTHON" scripts/watch-lsp.py &
"$PYTHON" -m uvicorn frlang.web.app:app --host 127.0.0.1 --port 8000 --reload --reload-dir frlang &
(cd web && npm run dev -- --host 127.0.0.1 --port 5173) &

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  DEV avec hot-reload : http://127.0.0.1:5173"
echo "  ─────────────────────────────────────────────────────"
echo "  Frontend (Vite HMR)  : port 5173 — rechargement auto"
echo "  Backend  (uvicorn)   : port 8000 — reload Python"
echo "  LSP      (WebSocket) : port 8765 — reload frlang/"
echo ""
echo "  ⚠  N'utilise PAS le port 8000 pour l'éditeur en dev"
echo "     (c'est l'API + build statique, pas de HMR ni /lsp)"
echo "═══════════════════════════════════════════════════════"
echo ""

wait
