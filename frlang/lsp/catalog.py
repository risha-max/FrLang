from __future__ import annotations

KEYWORDS: tuple[str, ...] = (
    "soit",
    "afficher",
    "definir",
    "fonction",
    "classe",
    "herite",
    "de",
    "constructeur",
    "retourne",
    "nouveau",
    "si",
    "sinon",
    "tantque",
    "pourchaque",
    "dans",
    "import",
    "from",
    "as",
    "vrai",
    "faux",
    "rien",
    "mod",
)

TYPES: tuple[str, ...] = (
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
    "Arbre",
    "Graphe",
)

BUILTINS: tuple[str, ...] = (
    "range",
    "adresse",
    "valeur",
    "type",
)

OBJECT_METHODS: dict[str, tuple[str, ...]] = {
    "Mots": ("inverser", "equals", "taille", "caractere", "concatener", "en_nombre"),
    "Rangee": ("ajouter", "element", "premier", "dernier", "taille", "contient", "vider"),
    "Sac": ("ajouter", "retirer", "taille", "contient", "vider"),
    "Carnet": ("etiqueter", "element", "contient", "etiquettes", "taille", "vider"),
    "Tas": ("empiler", "depiler", "taille", "vide"),
    "File": ("enfiler", "defiler", "taille", "vide"),
    "Fichier": ("ecrire", "lire", "lire_ligne", "fermer", "existe", "chemin", "taille"),
    "Arbre": ("valeur", "ajouter_enfant", "enfant", "nombre_enfants", "taille", "feuille"),
    "Graphe": ("ajouter_sommet", "lier", "voisins", "contient_sommet", "nombre_sommets", "nombre_aretes"),
    "Original": ("afficher", "equals"),
}

METHOD_SNIPPETS: dict[str, str] = {
    "ajouter": "ajouter($0)",
    "element": "element($0)",
    "caractere": "caractere($0)",
    "concatener": "concatener($0)",
    "equals": "equals($0)",
    "etiqueter": "etiqueter($0, $1)",
    "range": "range($0)",
    "adresse": "adresse($0)",
    "valeur": "valeur($0)",
    "type": "type($0)",
}
