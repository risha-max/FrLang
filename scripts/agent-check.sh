#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="python"
if [[ -x .venv/bin/python ]]; then
  PYTHON=".venv/bin/python"
fi

"$PYTHON" -m pytest tests/ -q
"$PYTHON" main.py "2 + 3 * 4" | grep -qx "14"
"$PYTHON" main.py "(1 + 2) * 3" | grep -qx "9"
"$PYTHON" main.py "2 ^ 3" | grep -qx "8"
"$PYTHON" main.py "10 mod 3" | grep -qx "1"
"$PYTHON" main.py "soit nombre x = 5; x + 2;" | grep -qx "7"
"$PYTHON" main.py "afficher soit nombre x = 5;" | grep -qx "5"
"$PYTHON" main.py "soit nombre x = 5; afficher x;" | grep -qx "5"
"$PYTHON" main.py "soit logique ok = vrai; afficher ok;" | grep -qx "vrai"
"$PYTHON" main.py 'soit Rangee n = nouveau Rangee(10, 20); n.ajouter(5); afficher n.taille();' | grep -qx "3"
"$PYTHON" main.py 'definir fonction double(nombre n) { retourne n * 2; } retourne nombre double(5);' | grep -qx "10"
"$PYTHON" main.py 'definir fonction incrementer(pointeur nombre p) { valeur(p) = valeur(p) + 1; } soit nombre x = 3; incrementer(adresse(x)); x;' | grep -qx "4"
"$PYTHON" -m pip install -e . -q
BINDIR="$("$PYTHON" -c "import os, sys; print(os.path.dirname(sys.executable))")"
FRBIN="$BINDIR/frlang"
IFRBIN="$BINDIR/ifrlang"
if [[ ! -x "$FRBIN" ]]; then
  FRBIN="$("$PYTHON" -c "import shutil; print(shutil.which('frlang') or '')")"
fi
if [[ ! -x "$IFRBIN" ]]; then
  IFRBIN="$("$PYTHON" -c "import shutil; print(shutil.which('ifrlang') or '')")"
fi
if [[ -z "$FRBIN" || -z "$IFRBIN" || ! -x "$FRBIN" || ! -x "$IFRBIN" ]]; then
  echo "agent-check: frlang/ifrlang introuvable après pip install -e ." >&2
  exit 1
fi
TMP_FR="$(mktemp --suffix=.fr)"
printf '%s\n' 'soit nombre x = 6; x + 1;' >"$TMP_FR"
"$FRBIN" "$TMP_FR" | grep -qx "7"
rm -f "$TMP_FR"
printf '2 + 2;\nquitter\n' | "$IFRBIN" | grep -Fq '4'

echo "agent-check: ok"
