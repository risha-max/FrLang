from __future__ import annotations

import re

_CLASS_PATTERN = re.compile(r"\bdefinir\s+classe\s+([A-Z]\w*)")
_FUNCTION_PATTERN = re.compile(r"\bdefinir\s+fonction\s+(\w+)")
_SOIT_PATTERN = re.compile(r"\bsoit\s+([A-Za-z]\w*)\s+(\w+)")

_BUILTIN_TYPES = {
    "nombre",
    "logique",
    "pointeur",
    "Mots",
    "Rangee",
    "Sac",
    "Carnet",
    "Tas",
    "File",
    "Fichier",
}


def extract_symbols(source: str) -> tuple[dict[str, str], set[str], set[str]]:
    """Retourne variables, fonctions et classes déclarées dans le fichier."""
    variables: dict[str, str] = {}
    functions: set[str] = set()
    classes: set[str] = set(_CLASS_PATTERN.findall(source))

    for var_type, name in _SOIT_PATTERN.findall(source):
        if var_type in _BUILTIN_TYPES or var_type[0].isupper():
            variables[name] = var_type

    functions.update(_FUNCTION_PATTERN.findall(source))
    return variables, functions, classes
