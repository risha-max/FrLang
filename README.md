# FrLang

Langage de programmation en français pour apprendre la programmation (primaire / secondaire).

FrLang utilise des mots du quotidien (`soit`, `afficher`, `definir`, `sac`, `rangée`, `carnet`…) plutôt que du jargon anglais.

## Exemple

```text
soit nombre x = 5;
afficher x;

definir double(n: nombre) {
    retourne n * 2;
} retourne nombre

double(3) + 4;
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Utilisation

```bash
python main.py "2 + 3 * 4"
python main.py
```

## Vérification

```bash
bash scripts/agent-check.sh
```

## Licence

À définir.
