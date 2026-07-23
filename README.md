# FrLang

Langage de programmation **en français** pour apprendre la logique et le code au primaire et au secondaire. Syntaxe proche du français parlé (`soit`, `afficher`, `definir`, `pourchaque`…) plutôt que du jargon anglais.

**Auteur :** Ilyas Lachhab — tuteur math & français, bac math UQAM.

## Exemple

```text
soit nombre x = 5;
afficher x;

definir fonction double(nombre n) {
    retourne n * 2;
} retourne nombre

double(3) + 4;
```

## Ce que fait le projet

Interpréteur Python complet avec REPL, CLI, exercices, serveur LSP et atelier web (Monaco + exécution).

| Domaine | Contenu |
|---------|---------|
| **Langage** | Variables, fonctions, classes, héritage, `si`/`sinon`, `tantque`, `pourchaque`, `arreter`/`continuer`, commentaires `//` et `/* */` |
| **Données** | `nombre`, `logique`, `Mots`, tableaux `nombre[n]`, collections (`Rangee`, `Sac`, `Carnet`, `Tas`, `File`, `Arbre`, `Graphe`, `Fichier`) |
| **Pointeurs** | `adresse`, `valeur`, arithmétique sur tableaux ; adresses mémoire réelles (ctypes) pour les primitives |
| **Modules** | `import` / `from … import` ; module intégré **`Math`** (`pi`, `e`, `phi`, `factorielle`, `random`) |
| **Entrée** | `demander()`, `lire()` |
| **Outils** | LSP (autocomplétion, hover, diagnostics), atelier web Vite/React/FastAPI |
| **Tests** | 235+ tests pytest + E2E Playwright |

## Fichiers importants

```
frlang/
  lexer.py          # Analyse lexicale (+ commentaires)
  parser.py         # Grammaire
  interpreter.py    # Exécution (cœur du langage)
  objects.py        # Types intégrés (Rangee, Sac, …)
  memory.py         # Stockage ctypes (adresses physiques)
  pointers.py       # Pointeurs
  imports.py        # Chargement de modules
  stdlib/math_module.py   # Module Math intégré
  cli.py            # Commande `frlang`
  lsp/              # Serveur Language Server (stdio + WebSocket)
  web/              # API FastAPI (run, sauvegarde main.frlang)

web/                # Atelier : éditeur Monaco, client LSP, exécution
probleme/           # Exercices (fizzbuzz, fibonacci, pointeurs, école, …)
tests/              # Suite de tests
main.py             # Point d'entrée CLI
scripts/agent-check.sh   # Vérification (tests + smoke)
scripts/web-dev.sh       # Dev atelier (ports 5173 / 8000 / 8765)
```

## Démarrage rapide

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
bash scripts/agent-check.sh
frlang probleme/fizzbuzz
```

Atelier web : `pip install -e ".[web,lsp]"` puis `bash scripts/web-dev.sh` → [http://127.0.0.1:5173](http://127.0.0.1:5173)

Comptes élèves (connexion simple, sans inscription) : édite `data/eleves.json` (modèle : `data/eleves.example.json`).

Comptes mock UI/UX : `bash scripts/seed-mocks.sh` puis `/login`
| Compte | Mot de passe | État |
|--------|--------------|------|
| `admin` | `admin` | Tuteur — métriques / progression |
| `nouveau` | `nouveau` | Élève 0% — parcours guidé |
| `encours` | `encours` | ~33% + leçon en cours |
| `avance` | `avance` | ~89% + stats riches |
| `demo` | `demo` | 1 leçon |

Parcours guidé : `data/curriculum.json`. Devoirs (problèmes assignables) : `data/devoirs.json`. Progression : `data/progress/<username>.json`.

## Licence

À définir.
