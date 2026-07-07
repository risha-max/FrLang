import pytest

from sac.errors import ParseError
from sac.interpreter import Interpreter


def test_adresse_and_valeur_primitive() -> None:
    result = Interpreter(
        "soit nombre x = 10; "
        "soit pointeur nombre p = adresse(x); "
        "valeur(p) = 20; "
        "x;"
    ).run()
    assert result == 20


def test_incrementer_with_pointer_param() -> None:
    result = Interpreter(
        "definir incrementer(p: pointeur nombre) { valeur(p) = valeur(p) + 1; } "
        "soit nombre x = 3; "
        "incrementer(adresse(x)); "
        "x;"
    ).run()
    assert result == 4


def test_pass_by_value_still_copies_object() -> None:
    result = Interpreter(
        "definir essayer(s: sac) { s.ajouter(99); } "
        "soit sac boite = sac [1]; essayer(boite); boite.taille();"
    ).run()
    assert result == 1


def test_pass_by_pointer_mutates_object() -> None:
    result = Interpreter(
        "definir remplir(p: pointeur sac) { valeur(p).ajouter(99); } "
        "soit sac boite = sac [1]; remplir(adresse(boite)); boite.taille();"
    ).run()
    assert result == 2


def test_adresse_requires_variable_name() -> None:
    with pytest.raises(ParseError, match="adresse\\(\\) a besoin"):
        Interpreter("adresse(5);").run()


def test_valeur_requires_pointer() -> None:
    with pytest.raises(ParseError, match="n'est pas un pointeur"):
        Interpreter("soit nombre x = 1; valeur(x);").run()


def test_pointer_type_mismatch_on_declaration() -> None:
    with pytest.raises(ParseError, match="doit viser"):
        Interpreter(
            "soit mots nom = \"Léa\"; "
            "soit pointeur nombre p = adresse(nom);"
        ).run()


def test_afficher_pointer_shows_hex_address() -> None:
    interpreter = Interpreter(
        "soit nombre x = 3; soit pointeur nombre p = adresse(x); afficher p;"
    )
    interpreter.run()
    assert len(interpreter.output) == 1
    assert interpreter.output[0].startswith("L'adresse hexadécimale de x est 0x")


def test_afficher_adresse_shows_hex_address() -> None:
    interpreter = Interpreter("soit nombre x = 3; afficher adresse(x);")
    interpreter.run()
    assert len(interpreter.output) == 1
    assert interpreter.output[0].startswith("L'adresse hexadécimale de x est 0x")


def test_bare_pointer_requires_valeur() -> None:
    with pytest.raises(ParseError, match="directement"):
        Interpreter("soit nombre x = 1; soit pointeur nombre p = adresse(x); p + 1;").run()


def test_pointer_operation_not_allowed_on_adresse_in_expression() -> None:
    with pytest.raises(ParseError, match="opération sur un pointeur"):
        Interpreter("soit nombre x = 1; adresse(x) + 1;").run()


def test_nested_pointer_not_allowed() -> None:
    with pytest.raises(ParseError, match="ne peut pas pointer vers un autre pointeur"):
        Interpreter("soit pointeur pointeur nombre p = adresse(x);").run()
