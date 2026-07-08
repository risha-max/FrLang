from __future__ import annotations

from frlang.lsp.catalog import BUILTINS, KEYWORDS, OBJECT_METHODS, TYPES

_KEYWORD_DOCS: dict[str, str] = {
    "soit": "Déclare une variable.\n\nExemple : `soit nombre age = 12;`",
    "afficher": "Affiche une valeur sur la sortie.\n\nExemple : `afficher 42;`",
    "definir": "Commence la définition d'une fonction ou d'une classe.",
    "fonction": "Mot-clé utilisé avec `definir` pour créer une fonction.",
    "classe": "Mot-clé utilisé avec `definir` pour créer une classe.",
    "herite": "Indique l'héritage d'une classe parente.",
    "de": "Utilisé avec `herite de` pour nommer la classe parente.",
    "constructeur": "Définit comment créer un objet de la classe.",
    "retourne": "Renvoie une valeur depuis une fonction.",
    "nouveau": "Crée un objet.\n\nExemple : `nouveau Rangee(1, 2, 3);`",
    "si": "Exécute un bloc seulement si la condition est vraie.",
    "sinon": "Bloc alternatif quand la condition du `si` est fausse.",
    "tantque": "Répète un bloc tant que la condition reste vraie.",
    "pourchaque": "Parcourt une collection.\n\nExemple : `pourchaque i dans range(5) { ... }`",
    "dans": "Utilisé avec `pourchaque` : `pourchaque x dans liste`.",
    "arreter": "Sort immédiatement de la boucle la plus proche.",
    "continuer": "Passe directement à l'itération suivante de la boucle.",
    "import": "Charge un autre fichier FrLang ou un module intégré (`Math`).",
    "from": "Importe un symbole précis : `from module import nom;`",
    "as": "Renomme un import : `import module as m;`",
    "vrai": "Valeur logique vraie.",
    "faux": "Valeur logique fausse.",
    "rien": "Valeur vide (comme `null`).",
    "mod": "Reste de la division entière.\n\nExemple : `10 mod 3` → 1",
}

_TYPE_DOCS: dict[str, str] = {
    "nombre": "Nombre entier ou décimal.",
    "logique": "Valeur booléenne : `vrai` ou `faux`.",
    "pointeur": "Adresse mémoire vers une variable ou un élément de tableau.",
    "Mots": "Texte (chaîne de caractères).",
    "Rangee": "Liste ordonnée. Les indices commencent à 0.",
    "Sac": "Ensemble sans doublons.",
    "Carnet": "Dictionnaire : étiquette → valeur.",
    "Tas": "Pile (LIFO) : dernier entré, premier sorti.",
    "File": "File d'attente (FIFO) : premier entré, premier sorti.",
    "Fichier": "Lecture et écriture sur le disque.",
    "Arbre": "Structure parent → enfants.",
    "Graphe": "Sommets reliés par des chemins.",
}

_BUILTIN_DOCS: dict[str, str] = {
    "range": "Génère une `Rangee` de nombres.\n\nExemples : `range(5)`, `range(2, 10)`, `range(0, 10, 2)`",
    "adresse": "Retourne l'adresse d'une variable : `adresse(x)`.",
    "valeur": "Lit ou écrit via un pointeur : `valeur(p)`.",
    "type": "Retourne le nom de la sorte d'une valeur.",
    "demander": "Lit une ligne de texte.\n\nExemples : `demander()`, `demander(\"Nom : \")`",
    "lire": "Lit une ligne et la convertit en nombre.\n\nExemples : `lire()`, `lire(\"Age : \")`",
}

_METHOD_DOCS: dict[str, dict[str, str]] = {
    "Mots": {
        "inverser": "Retourne le texte à l'envers.",
        "equals": "Compare deux textes.",
        "taille": "Nombre de caractères.",
        "caractere": "Caractère à la position (à partir de 1).",
        "concatener": "Colle deux textes.",
        "en_nombre": "Convertit un texte en nombre.",
    },
    "Rangee": {
        "ajouter": "Ajoute un élément à la fin.",
        "element": "Lit l'élément à la position (à partir de 0).",
        "premier": "Premier élément.",
        "dernier": "Dernier élément.",
        "taille": "Nombre d'éléments.",
        "contient": "Vérifie la présence d'une valeur.",
        "vider": "Vide la liste.",
    },
    "Sac": {
        "ajouter": "Ajoute un élément (sans doublon).",
        "retirer": "Retire un élément.",
        "taille": "Nombre d'éléments distincts.",
        "contient": "Vérifie la présence.",
        "vider": "Vide le sac.",
    },
    "Carnet": {
        "etiqueter": "Associe une étiquette à une valeur.",
        "element": "Lit la valeur d'une étiquette.",
        "contient": "Vérifie si l'étiquette existe.",
        "etiquettes": "Liste des étiquettes.",
        "taille": "Nombre d'entrées.",
        "vider": "Vide le carnet.",
    },
    "Tas": {
        "empiler": "Ajoute sur la pile.",
        "depiler": "Retire le dernier ajouté.",
        "taille": "Nombre d'éléments.",
        "vide": "Vrai si la pile est vide.",
    },
    "File": {
        "enfiler": "Ajoute à la file.",
        "defiler": "Retire le premier arrivé.",
        "taille": "Nombre d'éléments.",
        "vide": "Vrai si la file est vide.",
    },
    "Fichier": {
        "ecrire": "Écrit une ligne dans le fichier.",
        "lire": "Lit tout le contenu.",
        "lire_ligne": "Lit une ligne (à partir de 1).",
        "fermer": "Ferme le fichier.",
        "existe": "Vrai si le fichier existe.",
        "chemin": "Chemin du fichier.",
        "taille": "Taille en octets.",
    },
    "Arbre": {
        "valeur": "Valeur du nœud.",
        "ajouter_enfant": "Ajoute un enfant et le retourne.",
        "enfant": "Enfant à la position (à partir de 1).",
        "nombre_enfants": "Nombre d'enfants directs.",
        "taille": "Nombre total de nœuds du sous-arbre.",
        "feuille": "Vrai si le nœud n'a pas d'enfant.",
    },
    "Graphe": {
        "ajouter_sommet": "Ajoute un sommet nommé.",
        "lier": "Relie deux sommets.",
        "voisins": "Voisins d'un sommet.",
        "contient_sommet": "Vérifie si le sommet existe.",
        "nombre_sommets": "Nombre de sommets.",
        "nombre_aretes": "Nombre d'arêtes.",
    },
    "Original": {
        "afficher": "Affiche la description de l'objet.",
        "equals": "Compare deux objets.",
    },
}


def has_documentation(word: str, receiver_type: str | None = None) -> bool:
    return lookup_documentation(word, receiver_type) is not None


def lookup_documentation(word: str, receiver_type: str | None = None) -> str | None:
    if receiver_type is not None:
        methods = _METHOD_DOCS.get(receiver_type, {})
        if word in methods:
            return f"**{receiver_type}.{word}**\n\n{methods[word]}"
        if word in OBJECT_METHODS.get(receiver_type, ()):
            return f"**{receiver_type}.{word}**"

    lowered = word.lower()
    if word in KEYWORDS or lowered in KEYWORDS:
        key = word if word in KEYWORDS else lowered
        return f"**{key}**\n\n{_KEYWORD_DOCS.get(key, 'Mot-clé FrLang.')}"
    if word in TYPES:
        return f"**{word}**\n\n{_TYPE_DOCS.get(word, 'Sorte intégrée FrLang.')}"
    if word in BUILTINS:
        return f"**{word}**\n\n{_BUILTIN_DOCS.get(word, 'Fonction intégrée.')}"
    if word in {"vrai", "faux", "rien"}:
        return lookup_documentation(word, None)
    return None
