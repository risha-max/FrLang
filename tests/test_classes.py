import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def test_class_with_default_original_afficher() -> None:
    interpreter = Interpreter(
        'definir classe Personne { soit Mots nom = "Léa"; } '
        "soit Personne p = nouveau Personne(); p.afficher();"
    )
    interpreter.run()
    assert interpreter.output == ['Personne { nom=Léa }']


def test_method_override() -> None:
    interpreter = Interpreter(
        'definir classe Personne { soit Mots nom = "Léa"; '
        'definir fonction afficher() { afficher nom; } } '
        'definir classe Etudiant herite de Personne { '
        'definir fonction afficher() { afficher "Étudiant:"; afficher nom; } } '
        "soit Etudiant e = nouveau Etudiant(); e.afficher();"
    )
    interpreter.run()
    assert interpreter.output == ["Étudiant:", "Léa"]


def test_inherited_field_via_method() -> None:
    result = Interpreter(
        "definir classe Animal { soit nombre pattes = 4; "
        "definir fonction lire_pattes() { retourne pattes; } retourne nombre } "
        "definir classe Chien herite de Animal { } "
        "soit Chien c = nouveau Chien(); c.lire_pattes();"
    ).run()
    assert result == 4


def test_custom_constructor() -> None:
    result = Interpreter(
        'definir classe Personne { soit Mots nom = "?"; '
        'constructeur(Mots prenom) { nom = prenom; } '
        'definir fonction lire_nom() { retourne nom; } retourne Mots } '
        'soit Personne p = nouveau Personne("Léa"); p.lire_nom();'
    ).run()
    assert result.text == "Léa"


def test_class_name_needs_capital() -> None:
    with pytest.raises(ParseError, match="majuscule"):
        Interpreter("definir classe personne { }").run()


def test_definir_requires_fonction_or_classe() -> None:
    with pytest.raises(ParseError, match="fonction ou classe"):
        Interpreter("definir double(nombre n) { retourne n; } retourne nombre").run()


def test_cannot_redefine_original() -> None:
    with pytest.raises(ParseError, match="Original"):
        Interpreter("definir classe Original { }").run()


def test_undefined_parent_class() -> None:
    with pytest.raises(ParseError, match="classe parente"):
        Interpreter("definir classe Enfant herite de Inconnue { }").run()


def test_duplicate_class_field() -> None:
    with pytest.raises(ParseError, match="attribut"):
        Interpreter("definir classe Boite { soit nombre x = 1; soit nombre x = 2; }").run()


def test_unknown_instance_method() -> None:
    with pytest.raises(ParseError, match="ne connaît pas"):
        Interpreter(
            'definir classe Vide { } soit Vide v = nouveau Vide(); v.inconnue();'
        ).run()
