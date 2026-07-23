#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p data/progress
cp -f data/eleves.example.json data/eleves.json
cp -f data/mocks/progress/*.json data/progress/

echo "Comptes mock prêts :"
echo "  admin   / admin     → métriques (tuteur)"
echo "  nouveau / nouveau   → 0% (débutant, parcours guidé)"
echo "  encours / encours   → ~33% (en cours)"
echo "  avance  / avance    → ~89% (presque fini)"
echo "  demo    / demo      → 1 leçon"
echo "Ouvre http://127.0.0.1:5173/login"
