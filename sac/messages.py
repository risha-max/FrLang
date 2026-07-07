"""Messages d'erreur courts et simples, pour les élèves."""

from sac.errors import LexerError, ParseError

_OPERATORS_HINT = "Tu peux utiliser : +  -  *  /  mod  ^  et des parenthèses ( )"
_STATEMENT_HINT = "N'oublie pas le ; à la fin. Exemple : soit nombre x = 5;"
_TYPES_HINT = "Les sortes possibles : nombre, mots, logique, rangée, sac, carnet, tas, file."


def unknown_word(word: str, line: int, column: int) -> LexerError:
    hint = _OPERATORS_HINT
    if word.lower() in {"modulo", "reste"}:
        hint = 'Pour le reste, écris mod. Exemple : 10 mod 3'
    elif word in {"entier", "reel"}:
        hint = "Écris plutôt nombre. Exemple : soit nombre age = 12;"
    elif word in {"vrai_faux", "booleen", "bool"}:
        hint = "Écris plutôt logique. Exemple : soit logique actif = vrai;"

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

    if symbol in {"nombre", "mots", "logique", "rangée", "sac", "carnet", "tas", "file"}:
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
            f"Avant « {found} », il manque la sorte (nombre, mots, etc.).",
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
    if var_type in {"rangée", "sac", "carnet", "tas", "file"}:
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
            return "Exemple : soit nombre age = 12;"
        case "mots":
            return 'Exemple : soit mots nom = "Léa";'
        case "logique":
            return "Exemple : soit logique actif = vrai;"
        case "rangée":
            return "Exemple : soit rangée notes = rangée [10, 20];"
        case "sac":
            return 'Exemple : soit sac fruits = sac ["pomme"];'
        case "carnet":
            return 'Exemple : soit carnet eleve = carnet [nom: "Léa"];'
        case "tas":
            return "Exemple : soit tas assiettes = tas [];"
        case "file":
            return "Exemple : soit file attente = file [];"
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
        hint="La première place d'une rangée est 1.",
    )


def sac_no_order_access(method: str, line: int, column: int) -> ParseError:
    return ParseError(
        f"Dans un sac, on ne peut pas utiliser « {method} ».",
        line=line,
        column=column,
        hint="Avec un sac, utilise ajouter, retirer ou contient.",
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
        case "rangée":
            return "Tu peux utiliser : ajouter, element, premier, dernier, taille, contient, vider."
        case "sac":
            return "Tu peux utiliser : ajouter, retirer, taille, contient, vider."
        case "carnet":
            return "Tu peux utiliser : etiqueter, element, contient, etiquettes, taille, vider."
        case "tas":
            return "Tu peux utiliser : empiler, depiler, taille, vide."
        case "file":
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
        hint="Utilise seulement valeur() pour lire ou modifier la variable pointée.",
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
        "Il manque le nom de la fonction après definir.",
        line=line,
        column=column,
        hint="Exemple : definir double(n: nombre) { ... }",
    )


def expected_parameter_list(line: int, column: int) -> ParseError:
    return ParseError(
        "Il manque la liste des paramètres entre ( ).",
        line=line,
        column=column,
        hint="Exemple : definir double(n: nombre) { ... }",
    )
