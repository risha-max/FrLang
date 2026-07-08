"""Messages d'erreur courts et simples, pour les élèves."""

from frlang.errors import LexerError, ParseError

_OPERATORS_HINT = "Tu peux utiliser : +  -  *  /  mod  ^  et des parenthèses ( )"
_STATEMENT_HINT = "N'oublie pas le ; à la fin. Exemple : soit nombre x = 5;"
_TYPES_HINT = "Les sortes possibles : nombre, logique, nombre[10], logique[5], Mots, Rangee, Sac, Carnet, Tas, File."
_OBJECT_TYPE_RENAMES = {
    "rangée": "Rangee",
    "sac": "Sac",
    "carnet": "Carnet",
    "tas": "Tas",
    "file": "File",
}


def unknown_word(word: str, line: int, column: int) -> LexerError:
    hint = _OPERATORS_HINT
    if word.lower() in {"modulo", "reste"}:
        hint = 'Pour le reste, écris mod. Exemple : 10 mod 3'
    elif word in {"entier", "reel"}:
        hint = "Écris plutôt nombre. Exemple : soit nombre age = 12;"
    elif word in {"vrai_faux", "booleen", "bool"}:
        hint = "Écris plutôt logique. Exemple : soit logique actif = vrai;"
    elif word == "tant":
        hint = "Écris plutôt tantque. Exemple : tantque i < 5 { somme = somme + i; }"
    elif word in _OBJECT_TYPE_RENAMES:
        new_name = _OBJECT_TYPE_RENAMES[word]
        hint = f"Les objets commencent par une majuscule. Écris plutôt {new_name}. Exemple : nouveau {new_name}();"

    return LexerError(
        f"Je ne connais pas ce mot : « {word} ».",
        line=line,
        column=column,
        hint=hint,
    )


def unknown_symbol(char: str, line: int, column: int) -> LexerError:
    return LexerError(
        f"Je ne connais pas ce signe : « {char} ».",
        line=line,
        column=column,
        hint=_OPERATORS_HINT,
    )


def invalid_number(raw: str, line: int, column: int) -> LexerError:
    return LexerError(
        f"Ce nombre est mal écrit : « {raw} ».",
        line=line,
        column=column,
        hint="Un nombre avec des décimales ressemble à 3.14",
    )


def incomplete_number(line: int, column: int) -> LexerError:
    return LexerError(
        "Il y a un point « . » mais pas de chiffres après.",
        line=line,
        column=column,
        hint="Exemple : 3.14",
    )


def invalid_binary_literal(content: str, line: int, column: int) -> LexerError:
    return LexerError(
        f"Ce nombre binaire est mal écrit : « b'{content}' ».",
        line=line,
        column=column,
        hint="Un nombre binaire utilise seulement 0 et 1. Exemple : b'1010'",
    )


def invalid_hex_literal(content: str, line: int, column: int) -> LexerError:
    return LexerError(
        f"Ce nombre hexadécimal est mal écrit : « h'{content}' ».",
        line=line,
        column=column,
        hint="Utilise 0-9 et a-f. Exemple : h'1A2B' ou h'10471284'",
    )


def empty_based_literal(base: str, line: int, column: int) -> LexerError:
    label = "binaire" if base == "binary" else "hexadécimal"
    example = "b'1010'" if base == "binary" else "h'1A'"
    return LexerError(
        f"Il manque des chiffres dans ce nombre {label}.",
        line=line,
        column=column,
        hint=f"Exemple : soit nombre x = {example};",
    )


def unknown_number_prefix(prefix: str, line: int, column: int) -> LexerError:
    return LexerError(
        f"Je ne connais pas « {prefix}'...' » pour un nombre.",
        line=line,
        column=column,
        hint="Pour un nombre, utilise b'...' (binaire) ou h'...' (hexadécimal).",
    )


def unterminated_number_literal(base: str, line: int, column: int) -> LexerError:
    label = base if base in {"b", "h"} else "nombre"
    return LexerError(
        f"Il manque une apostrophe « ' » pour fermer ce nombre.",
        line=line,
        column=column,
        hint="Exemple : soit nombre x = b'1010';",
    )


def empty_program() -> ParseError:
    return ParseError(
        "Tu n'as rien écrit.",
        line=1,
        column=1,
        hint="Écris quelque chose, par exemple : soit nombre x = 5;",
    )


def empty_expression() -> ParseError:
    return empty_program()


def incomplete_expression(line: int, column: int) -> ParseError:
    return ParseError(
        "Ton calcul n'est pas fini.",
        line=line,
        column=column,
        hint="Après + ou *, il faut un nombre. Exemple : 2 + 3",
    )


def unexpected_symbol(symbol: str, line: int, column: int) -> ParseError:
    if symbol == ")":
        message = "Il y a une « ) » de trop."
        hint = "Chaque « ( » doit avoir sa « ) »."
    elif symbol == "(":
        message = "Cette « ( » est au mauvais endroit."
        hint = "Les parenthèses regroupent un calcul : (2 + 3) * 4"
    elif symbol == ";":
        message = "Ce « ; » est au mauvais endroit."
        hint = _STATEMENT_HINT
    elif symbol == "=":
        message = "Ce « = » est au mauvais endroit."
        hint = "Pour créer un nom, écris : soit nombre score = 5;"
    else:
        message = f"Le signe « {symbol} » est au mauvais endroit."
        hint = _OPERATORS_HINT

    return ParseError(message, line=line, column=column, hint=hint)


def missing_closing_paren(line: int, column: int) -> ParseError:
    return ParseError(
        "Il manque une « ) ».",
        line=line,
        column=column,
        hint="Ferme la parenthèse ouverte avec « ) ».",
    )


def unterminated_text(line: int, column: int) -> LexerError:
    return LexerError(
        'Il manque un guillemet « " » à la fin du texte.',
        line=line,
        column=column,
        hint='Le texte va entre guillemets : "Bonjour"',
    )


def missing_value_after_equal(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Tu as oublié la valeur de « {name} » après le =.",
        line=line,
        column=column,
        hint=f"Exemple : soit nombre {name} = 5;",
    )


def empty_statement(line: int, column: int) -> ParseError:
    return ParseError(
        "Cette ligne est vide.",
        line=line,
        column=column,
        hint="Écris quelque chose avant le ;. Exemple : afficher 2 + 3;",
    )


def unexpected_operator(symbol: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"On ne peut pas commencer par « {symbol} ».",
        line=line,
        column=column,
        hint="Commence par un nombre, un nom ou « ( ».",
    )


def expected_value(symbol: str, line: int, column: int) -> ParseError:
    if symbol in {"+", "*", "/", "^"}:
        return unexpected_operator(symbol, line, column)

    if symbol == ";":
        return empty_statement(line, column)

    if symbol in {"vrai", "faux"}:
        return ParseError(
            f"« {symbol} » ne va pas ici.",
            line=line,
            column=column,
            hint="Exemple : soit logique actif = vrai;",
        )

    if symbol in {"nombre", "logique", "Mots", "Rangee", "Sac", "Carnet", "Tas", "File"}:
        return type_in_expression(symbol, line, column)

    return ParseError(
        f"J'attendais un nombre ou un nom, pas « {symbol} ».",
        line=line,
        column=column,
        hint="Écris un nombre, un nom ou « ( ».",
    )


def missing_semicolon(line: int, column: int) -> ParseError:
    return ParseError(
        "Il manque un ; à la fin de la ligne.",
        line=line,
        column=column,
        hint=_STATEMENT_HINT,
    )


def expected_type(line: int, column: int, *, found: str | None = None) -> ParseError:
    if found is not None:
        return ParseError(
            f"Avant « {found} », il manque la sorte (nombre, Mots, etc.).",
            line=line,
            column=column,
            hint="Exemple : soit nombre x = 5;",
        )

    return ParseError(
        "Après soit, il faut dire quelle sorte c'est.",
        line=line,
        column=column,
        hint=f"{_TYPES_HINT} Exemple : soit nombre age = 12;",
    )


def missing_type_before_name(name: str, line: int, column: int) -> ParseError:
    return expected_type(line, column, found=name)


def type_as_variable_name(type_name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"« {type_name} » est un mot spécial, pas un nom.",
        line=line,
        column=column,
        hint="Choisis un nom, comme x, score ou prenom.",
    )


def type_in_expression(type_name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"« {type_name} » est un mot spécial, pas un nom à utiliser ici.",
        line=line,
        column=column,
        hint="Utilise le nom que tu as choisi, par exemple x.",
    )


def expected_variable_name(line: int, column: int) -> ParseError:
    return ParseError(
        "Il manque le nom.",
        line=line,
        column=column,
        hint="Exemple : soit nombre age = 12;",
    )


def expected_equal(line: int, column: int) -> ParseError:
    return ParseError(
        "Il manque le signe = .",
        line=line,
        column=column,
        hint="Exemple : soit nombre score = 10;",
    )


def use_soit_for_declaration(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Pour créer « {name} », commence par soit.",
        line=line,
        column=column,
        hint=f"Exemple : soit nombre {name} = 5;",
    )


def variable_already_defined(
    name: str,
    existing_type: str,
    new_type: str,
    line: int,
    column: int,
) -> ParseError:
    if existing_type == new_type:
        message = f"Tu as déjà créé « {name} »."
        hint = f"Tu ne peux pas le créer deux fois. Utilise « {name} » ou choisis un autre nom."
    else:
        message = f"« {name} » existe déjà (c'est un {existing_type})."
        hint = f"Tu ne peux pas en faire un {new_type}. Choisis un autre nom."

    return ParseError(message, line=line, column=column, hint=hint)


def undefined_variable(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Je ne connais pas « {name} ».",
        line=line,
        column=column,
        hint=f"Crée-le d'abord : soit nombre {name} = 0;",
    )


def type_mismatch(
    name: str,
    expected: str,
    got: str,
    line: int,
    column: int,
) -> ParseError:
    return ParseError(
        f"Pour « {name} », il faut un {expected}, pas un {got}.",
        line=line,
        column=column,
        hint=_type_hint(expected),
    )


def wrong_type_in_expression(var_type: str, line: int, column: int) -> ParseError:
    if var_type in {"Mots", "Rangee", "Sac", "Carnet", "Tas", "File"}:
        return object_in_numeric_expression(var_type, line, column)

    return ParseError(
        f"On ne peut pas faire de calcul avec un {var_type}.",
        line=line,
        column=column,
        hint="Les calculs marchent avec des nombres.",
    )


def _type_hint(var_type: str) -> str:
    match var_type:
        case "nombre":
            return "Exemple : soit nombre age = 12; ou b'1010'; ou h'1A';"
        case "Mots":
            return 'Exemple : soit Mots nom = nouveau Mots("Léa"); ou soit Mots nom = "Léa";'
        case "logique":
            return "Exemple : soit logique actif = vrai;"
        case "Rangee":
            return "Exemple : soit Rangee notes = nouveau Rangee(10, 20);"
        case "Sac":
            return 'Exemple : soit Sac fruits = nouveau Sac("pomme");'
        case "Carnet":
            return 'Exemple : soit Carnet eleve = nouveau Carnet(nom: "Léa");'
        case "Tas":
            return "Exemple : soit Tas assiettes = nouveau Tas();"
        case "File":
            return "Exemple : soit File attente = nouveau File();"
        case str() if var_type.startswith("pointeur "):
            return f"Exemple : soit {var_type} p = adresse(x);"
        case _:
            return "Regarde l'exemple et réessaie."


def division_by_zero(line: int, column: int) -> ParseError:
    return ParseError(
        "On ne peut pas diviser par zéro.",
        line=line,
        column=column,
        hint="Change le nombre après / .",
    )


def modulo_by_zero(line: int, column: int) -> ParseError:
    return ParseError(
        "On ne peut pas faire mod avec zéro.",
        line=line,
        column=column,
        hint="Le nombre après mod doit être différent de 0.",
    )


def unknown_object_method(obj_type: str, method: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Un {obj_type} ne connaît pas « {method} ».",
        line=line,
        column=column,
        hint=_object_methods_hint(obj_type),
    )


def wrong_method_argument_count(
    method: str,
    expected: int,
    got: int,
    line: int,
    column: int,
) -> ParseError:
    if expected == 0:
        detail = f"« {method} » ne prend rien entre les parenthèses."
    elif expected == 1:
        detail = f"« {method} » a besoin d'une valeur entre les parenthèses."
    else:
        detail = f"« {method} » a besoin de {expected} valeurs entre les parenthèses."

    return ParseError(
        detail,
        line=line,
        column=column,
        hint="Regarde les ( ) après le point.",
    )


def index_out_of_range(
    obj_type: str,
    position: object,
    size: int,
    line: int,
    column: int,
) -> ParseError:
    return ParseError(
        f"La place {position} n'existe pas (il y en a {size}).",
        line=line,
        column=column,
        hint="La première place d'une Rangee est 1.",
    )


def sac_no_order_access(method: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Dans un Sac, on ne peut pas utiliser « {method} ».",
        line=line,
        column=column,
        hint="Avec un Sac, utilise ajouter, retirer ou contient.",
    )


def carnet_key_missing(key: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"L'étiquette « {key} » n'est pas dans le carnet.",
        line=line,
        column=column,
        hint='Ajoute-la avec etiqueter, par exemple : c.etiqueter("score", 10)',
    )


def empty_collection(obj_type: str, method: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Le {obj_type} est vide, donc « {method} » ne marche pas.",
        line=line,
        column=column,
        hint=f"Ajoute d'abord quelque chose dans le {obj_type}.",
    )


def object_in_numeric_expression(obj_type: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"On ne peut pas faire de calcul avec un {obj_type}.",
        line=line,
        column=column,
        hint="Utilise un point, par exemple : notes.taille()",
    )


def expected_method_name(line: int, column: int) -> ParseError:
    return ParseError(
        "Après le point, il faut un nom d'action.",
        line=line,
        column=column,
        hint='Exemple : fruits.ajouter("pomme")',
    )


def expected_method_parentheses(method: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Après « {method} », il faut des parenthèses ( ).",
        line=line,
        column=column,
        hint=f"Exemple : notes.{method}()",
    )


def _object_methods_hint(obj_type: str) -> str:
    match obj_type:
        case "Mots":
            return "Tu peux utiliser : inverser, equals."
        case "Rangee":
            return "Tu peux utiliser : ajouter, element, premier, dernier, taille, contient, vider."
        case "Sac":
            return "Tu peux utiliser : ajouter, retirer, taille, contient, vider."
        case "Carnet":
            return "Tu peux utiliser : etiqueter, element, contient, etiquettes, taille, vider."
        case "Tas":
            return "Tu peux utiliser : empiler, depiler, taille, vide."
        case "File":
            return "Tu peux utiliser : enfiler, defiler, taille, vide."
        case _:
            return "Vérifie le mot après le point."


def function_already_defined(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"La fonction « {name} » existe déjà.",
        line=line,
        column=column,
        hint="Choisis un autre nom pour cette fonction.",
    )


def undefined_function(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Je ne connais pas la fonction « {name} ».",
        line=line,
        column=column,
        hint="Écris definir avant de l'appeler.",
    )


def missing_closing_brace(line: int, column: int) -> ParseError:
    return ParseError(
        "Il manque une « } » pour fermer la fonction.",
        line=line,
        column=column,
        hint="Ferme le bloc avec « } ».",
    )


def expected_return_type(line: int, column: int) -> ParseError:
    return ParseError(
        "Il manque ce que la fonction retourne après « } ».",
        line=line,
        column=column,
        hint="Exemple : } retourne nombre",
    )


def unexpected_return_type(line: int, column: int) -> ParseError:
    return ParseError(
        "Cette fonction ne retourne rien — enlève « retourne ... » après « } ».",
        line=line,
        column=column,
        hint="Exemple : definir dire() { afficher 1; }",
    )


def return_outside_function(line: int, column: int) -> ParseError:
    return ParseError(
        "« retourne » ne peut être utilisé que dans une fonction.",
        line=line,
        column=column,
        hint="Écris retourne seulement entre { } d'une fonction.",
    )


def expected_logique_condition(line: int, column: int) -> ParseError:
    return ParseError(
        "J'attendais une condition (vrai, faux, comparaison ou appel logique).",
        line=line,
        column=column,
        hint="Exemple : si x < 10 { ... } ou si vrai { ... }",
    )


def missing_return_statement(return_type: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Cette fonction doit retourner un {return_type}.",
        line=line,
        column=column,
        hint="Ajoute : retourne ...; avant la fin du bloc.",
    )


def return_in_void_function(line: int, column: int) -> ParseError:
    return ParseError(
        "Cette fonction ne retourne rien.",
        line=line,
        column=column,
        hint="Enlève « retourne » ou ajoute un type après « } ».",
    )


def wrong_function_argument_count(name: str, expected: int, got: int, line: int, column: int) -> ParseError:
    return ParseError(
        f"La fonction « {name} » veut {expected} valeur(s), pas {got}.",
        line=line,
        column=column,
        hint="Regarde les valeurs entre les parenthèses.",
    )


def ref_argument_requires_name(param: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"« {param} » a besoin d'un pointeur (adresse), pas d'un calcul.",
        line=line,
        column=column,
        hint="Exemple : incrementer(adresse(x)) et non incrementer(5)",
    )


def adresse_requires_variable(line: int, column: int) -> ParseError:
    return ParseError(
        "adresse() a besoin d'un nom de variable.",
        line=line,
        column=column,
        hint="Exemple : adresse(x) et non adresse(5)",
    )


def type_requires_argument(line: int, column: int) -> ParseError:
    return ParseError(
        "type() a besoin d'une valeur.",
        line=line,
        column=column,
        hint="Exemple : type(x) ou type(5)",
    )


def type_wrong_argument_count(line: int, column: int) -> ParseError:
    return ParseError(
        "type() ne prend qu'une seule valeur.",
        line=line,
        column=column,
        hint="Exemple : type(x) et non type(x, y)",
    )


def not_a_pointer(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"« {name} » n'est pas un pointeur.",
        line=line,
        column=column,
        hint="Utilise valeur() seulement sur un pointeur.",
    )


def expected_type_after_pointeur(line: int, column: int) -> ParseError:
    return ParseError(
        "Il manque le type après pointeur.",
        line=line,
        column=column,
        hint="Exemple : soit pointeur nombre p = adresse(x);",
    )


def nested_pointer_not_allowed(line: int, column: int) -> ParseError:
    return ParseError(
        "Un pointeur ne peut pas pointer vers un autre pointeur.",
        line=line,
        column=column,
        hint="Exemple : soit pointeur nombre p = adresse(x);",
    )


def pointer_requires_valeur(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"On ne peut pas utiliser « {name} » directement.",
        line=line,
        column=column,
        hint="Utilise valeur() pour lire ou modifier ce qu'il pointe.",
    )


def pointer_operation_not_allowed(line: int, column: int) -> ParseError:
    return ParseError(
        "On ne peut pas faire d'opération sur un pointeur.",
        line=line,
        column=column,
        hint="Pour un tableau primitif, utilise pointeur + 1 puis valeur(). Sinon, utilise seulement valeur().",
    )


def pointer_arithmetic_requires_array(line: int, column: int) -> ParseError:
    return ParseError(
        "L'arithmétique de pointeur ne fonctionne que sur un tableau primitif.",
        line=line,
        column=column,
        hint="Exemple : soit pointeur nombre p = adresse(notes); valeur(p + 1);",
    )


def pointer_offset_requires_integer(line: int, column: int) -> ParseError:
    return ParseError(
        "Le décalage d'un pointeur doit être un entier positif.",
        line=line,
        column=column,
        hint="Exemple : valeur(p + 1);",
    )


def pointer_cannot_target_array_type(line: int, column: int) -> ParseError:
    return ParseError(
        "Un pointeur ne peut pas viser directement un tableau primitif.",
        line=line,
        column=column,
        hint="Utilise adresse(notes) pour obtenir un pointeur vers le premier élément.",
    )


def array_type_requires_primitive(element_type: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Seuls nombre et logique peuvent former un tableau primitif, pas « {element_type} ».",
        line=line,
        column=column,
        hint="Exemple : soit nombre[10] notes = [10, 20, 30];",
    )


def missing_closing_bracket(line: int, column: int) -> ParseError:
    return ParseError(
        "Il manque un crochet fermant « ] ».",
        line=line,
        column=column,
        hint="Exemple : soit nombre[10] notes = [10, 20, 30];",
    )


def array_index_out_of_bounds(index: int, size: int, line: int, column: int) -> ParseError:
    return ParseError(
        f"L'indice {index} est hors limites pour un tableau de taille {size}.",
        line=line,
        column=column,
        hint="Les indices commencent à 0 pour le premier élément.",
    )


def array_size_required(line: int, column: int) -> ParseError:
    return ParseError(
        "Un tableau primitif a besoin d'une taille entre les crochets.",
        line=line,
        column=column,
        hint="Exemple : soit nombre[10] notes = [1, 2, 3];",
    )


def array_size_must_be_constant(line: int, column: int) -> ParseError:
    return ParseError(
        "La taille d'un tableau doit être un nombre connu à l'avance.",
        line=line,
        column=column,
        hint="Écris un nombre entier positif, par exemple : soit nombre[10] notes = [];",
    )


def array_size_invalid(size: int, line: int, column: int) -> ParseError:
    return ParseError(
        f"La taille d'un tableau doit être un entier positif, pas {size}.",
        line=line,
        column=column,
        hint="Exemple : soit nombre[10] notes = [1, 2];",
    )


def array_too_many_elements(got: int, size: int, line: int, column: int) -> ParseError:
    return ParseError(
        f"Tu as donné {got} valeurs, mais le tableau ne peut en contenir que {size}.",
        line=line,
        column=column,
        hint="Enlève des valeurs ou augmente la taille entre les crochets.",
    )


def pointer_type_mismatch(
    name: str,
    expected_target: str,
    got_target: str,
    line: int,
    column: int,
) -> ParseError:
    return ParseError(
        f"Ce pointeur doit viser un {expected_target}, pas un {got_target}.",
        line=line,
        column=column,
        hint=f"Exemple : soit pointeur {expected_target} p = adresse(nom);",
    )


def assign_to_undefined(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Je ne connais pas « {name} » pour lui donner une valeur.",
        line=line,
        column=column,
        hint=f"Crée-le d'abord avec : soit nombre {name} = 0;",
    )


def expected_function_name(line: int, column: int) -> ParseError:
    return ParseError(
        "Il manque le nom de la fonction après fonction.",
        line=line,
        column=column,
        hint="Exemple : definir fonction double(nombre n) { ... }",
    )


def expected_parameter_list(line: int, column: int) -> ParseError:
    return ParseError(
        "Il manque la liste des paramètres entre ( ).",
        line=line,
        column=column,
        hint="Exemple : definir fonction double(nombre n) { ... }",
    )


def expected_fonction_or_classe(line: int, column: int) -> ParseError:
    return ParseError(
        "Après definir, écris fonction ou classe.",
        line=line,
        column=column,
        hint="Exemple : definir fonction dire() { ... } ou definir classe Personne { ... }",
    )


def expected_class_name(line: int, column: int) -> ParseError:
    return ParseError(
        "Il manque le nom de la classe après classe.",
        line=line,
        column=column,
        hint="Exemple : definir classe Personne { ... }",
    )


def class_already_defined(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"La classe « {name} » existe déjà.",
        line=line,
        column=column,
        hint="Choisis un autre nom pour cette classe.",
    )


def undefined_class(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Je ne connais pas la classe « {name} ».",
        line=line,
        column=column,
        hint="Écris definir classe avant de l'utiliser.",
    )


def cannot_redefine_original(line: int, column: int) -> ParseError:
    return ParseError(
        "La classe Original existe déjà — tu ne peux pas la redéfinir.",
        line=line,
        column=column,
        hint="Toutes les classes héritent déjà de Original.",
    )


def undefined_parent_class(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Je ne connais pas la classe parente « {name} ».",
        line=line,
        column=column,
        hint="Crée la classe parente avant, ou enlève herite de.",
    )


def inheritance_cycle(name: str, parent: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"« {name} » ne peut pas hériter de « {parent} » (boucle).",
        line=line,
        column=column,
        hint="Vérifie la chaîne herite de.",
    )


def duplicate_class_field(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"L'attribut « {name} » est déjà dans cette classe.",
        line=line,
        column=column,
        hint="Choisis un autre nom pour cet attribut.",
    )


def duplicate_class_method(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"La fonction « {name} » est déjà dans cette classe.",
        line=line,
        column=column,
        hint="Une seule fonction par nom dans la même classe.",
    )


def unexpected_in_class(token: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Je ne comprends pas « {token} » dans cette classe.",
        line=line,
        column=column,
        hint="Dans une classe, tu peux écrire : soit ... = ...; ou definir fonction ...",
    )


def unknown_instance_method(class_name: str, method: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"La classe « {class_name} » ne connaît pas « {method} ».",
        line=line,
        column=column,
        hint="Vérifie le nom de la fonction après le point.",
    )


def unknown_instance_field(class_name: str, field: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"La classe « {class_name} » n'a pas d'attribut « {field} ».",
        line=line,
        column=column,
        hint="Vérifie le nom après le point.",
    )


def rien_not_allowed_for_type(var_type: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"« rien » ne convient pas pour un {var_type}.",
        line=line,
        column=column,
        hint="Utilise rien seulement pour nombre, logique ou pointeur.",
    )


def nothing_value_not_allowed(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"« {name} » vaut rien — il faut d'abord lui donner une valeur.",
        line=line,
        column=column,
        hint="Écris une valeur avec = avant de l'utiliser.",
    )


def expected_herite_de(line: int, column: int) -> ParseError:
    return ParseError(
        "Après herite, il faut écrire de et le nom de la classe.",
        line=line,
        column=column,
        hint="Exemple : definir classe Enfant herite de Parent { ... }",
    )


def use_nouveau_to_create(type_name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Pour créer un {type_name}, écris : nouveau {type_name}()",
        line=line,
        column=column,
        hint=f"Exemple : soit {type_name} boite = nouveau {type_name}();",
    )


def deprecated_object_literal_syntax(type_name: str, line: int, column: int) -> ParseError:
    modern = _OBJECT_TYPE_RENAMES.get(type_name, type_name)
    return ParseError(
        f"On ne crée plus un {modern} avec des crochets [ ].",
        line=line,
        column=column,
        hint=f"Écris plutôt : nouveau {modern}() ou nouveau {modern}(1, 2)",
    )


def object_name_needs_capital(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Le nom d'objet « {name} » doit commencer par une majuscule.",
        line=line,
        column=column,
        hint="Exemple : definir classe Personne { ... } ou nouveau Rangee();",
    )


def expected_type_after_nouveau(line: int, column: int) -> ParseError:
    return ParseError(
        "Après nouveau, il faut le nom de l'objet à créer.",
        line=line,
        column=column,
        hint="Exemple : nouveau Rangee() ou nouveau Personne();",
    )


def no_matching_constructor(class_name: str, argc: int, line: int, column: int) -> ParseError:
    if argc == 0:
        hint = f"Ajoute constructeur() dans la classe {class_name}, ou enlève les arguments."
    else:
        hint = f"Vérifie le constructeur de {class_name} (nombre d'arguments)."
    return ParseError(
        f"Aucun constructeur de {class_name} ne correspond à {argc} argument(s).",
        line=line,
        column=column,
        hint=hint,
    )


def duplicate_class_constructor(argc: int, line: int, column: int) -> ParseError:
    return ParseError(
        f"Il y a déjà un constructeur avec {argc} argument(s).",
        line=line,
        column=column,
        hint="Chaque constructeur doit avoir un nombre d'arguments différent.",
    )


def wrong_constructor_argument_count(
    type_name: str,
    expected: int,
    got: int,
    line: int,
    column: int,
) -> ParseError:
    return ParseError(
        f"Le constructeur de {type_name} ne prend pas {got} argument(s) comme ça.",
        line=line,
        column=column,
        hint=f"Exemple : nouveau {type_name}() pour un objet vide.",
    )


def expected_dans_after_pourchaque(line: int, column: int) -> ParseError:
    return ParseError(
        "Après le nom de variable, il faut écrire dans.",
        line=line,
        column=column,
        hint="Exemple : pourchaque i dans range(5) { afficher i; }",
    )


def not_a_collection(got: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Pour pourchaque, il faut une Collection, pas un {got}.",
        line=line,
        column=column,
        hint="Utilise Rangee, Sac, Carnet, Tas, File ou range(...).",
    )


def range_wrong_argument_count(got: int, line: int, column: int) -> ParseError:
    return ParseError(
        f"range() prend 1, 2 ou 3 nombres, pas {got}.",
        line=line,
        column=column,
        hint="Exemples : range(10); range(2, 10); range(0, 10, 2);",
    )


def range_requires_integer(name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Pour range(), « {name} » doit être un nombre entier.",
        line=line,
        column=column,
        hint="Exemple : range(5) ou range(0, 10, 2);",
    )


def range_step_cannot_be_zero(line: int, column: int) -> ParseError:
    return ParseError(
        "Le pas de range() ne peut pas être zéro.",
        line=line,
        column=column,
        hint="Utilise un pas différent de 0.",
    )


def import_requires_module_name(line: int, column: int) -> ParseError:
    return ParseError(
        "Après import, il faut le nom du fichier à charger.",
        line=line,
        column=column,
        hint='Exemple : import utilitaires; ou import "dossier/module";',
    )


def import_requires_name(line: int, column: int) -> ParseError:
    return ParseError(
        "Après import, il faut dire quoi importer.",
        line=line,
        column=column,
        hint="Exemple : from utilitaires import saluer;",
    )


def import_requires_from(line: int, column: int) -> ParseError:
    return ParseError(
        "Pour importer un nom précis, commence par from.",
        line=line,
        column=column,
        hint="Exemple : from utilitaires import saluer;",
    )


def import_requires_import_keyword(line: int, column: int) -> ParseError:
    return ParseError(
        "Après from, il faut écrire import.",
        line=line,
        column=column,
        hint="Exemple : from utilitaires import saluer;",
    )


def import_file_not_found(
    module_name: str,
    line: int,
    column: int,
    *,
    detail: str | None = None,
) -> ParseError:
    message = f"Je ne trouve pas le fichier « {module_name} »."
    if detail:
        message = f"{message} ({detail})"
    return ParseError(
        message,
        line=line,
        column=column,
        hint="Le fichier doit être à côté du programme ou dans le dossier courant.",
    )


def circular_import(chain: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Import circulaire : {chain}.",
        line=line,
        column=column,
        hint="Deux fichiers s'importent l'un l'autre. Réorganise le code.",
    )


def import_name_not_found(module_name: str, name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"« {name} » n'existe pas dans « {module_name} ».",
        line=line,
        column=column,
        hint="Vérifie l'orthographe ou définis ce nom dans le fichier importé.",
    )


def import_name_not_exported(module_name: str, name: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Le module « {module_name} » n'a pas de méthode « {name} ».",
        line=line,
        column=column,
        hint="Utilise from ... import pour les fonctions et variables du module.",
    )


def import_class_alias_not_supported(line: int, column: int) -> ParseError:
    return ParseError(
        "On ne peut pas encore renommer une classe importée avec as.",
        line=line,
        column=column,
        hint="Écris plutôt : from module import MaClasse;",
    )


def import_module_attribute_not_found(
    module_name: str,
    name: str,
    line: int,
    column: int,
) -> ParseError:
    return ParseError(
        f"« {module_name}.{name} » n'existe pas.",
        line=line,
        column=column,
        hint="Vérifie le nom dans le fichier importé.",
    )

