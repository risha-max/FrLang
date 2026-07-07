import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def test_type_primitive_literals() -> None:
    assert Interpreter("type(5);").run() == "nombre"
    assert Interpreter('type("salut");').run() == "Mots"
    assert Interpreter("type(vrai);").run() == "logique"


def test_type_primitive_variable() -> None:
    assert Interpreter("soit nombre x = 5; type(x);").run() == "nombre"
    assert Interpreter('soit Mots s = "a"; type(s);').run() == "Mots"
    assert Interpreter("soit logique ok = faux; type(ok);").run() == "logique"


def test_type_builtin_objects() -> None:
    assert Interpreter("soit Sac boite = nouveau Sac(1); type(boite);").run() == "Sac"
    assert Interpreter("type(nouveau Sac(1, 2));").run() == "Sac"
    assert Interpreter("type(nouveau Rangee(1));").run() == "Rangee"


def test_type_user_class() -> None:
    assert (
        Interpreter(
            'definir classe Personne { soit Mots nom = "Léa"; } '
            "soit Personne p = nouveau Personne(); type(p);"
        ).run()
        == "Personne"
    )
    assert (
        Interpreter(
            'definir classe Personne { soit Mots nom = "Léa"; } type(nouveau Personne());'
        ).run()
        == "Personne"
    )


def test_type_pointer() -> None:
    assert (
        Interpreter("soit nombre x = 1; soit pointeur nombre p = adresse(x); type(p);").run()
        == "pointeur nombre"
    )
    assert (
        Interpreter("soit nombre x = 1; type(adresse(x));").run() == "pointeur nombre"
    )


def test_type_in_afficher() -> None:
    interpreter = Interpreter("soit nombre x = 5; afficher type(x);")
    interpreter.run()
    assert interpreter.output == ["nombre"]


def test_type_requires_argument() -> None:
    with pytest.raises(ParseError, match="type\\(\\) a besoin"):
        Interpreter("type();").run()


def test_type_wrong_argument_count() -> None:
    with pytest.raises(ParseError, match="ne prend qu'une seule"):
        Interpreter("type(1, 2);").run()


def test_type_undefined_variable() -> None:
    with pytest.raises(ParseError, match="Je ne connais pas"):
        Interpreter("type(inconnue);").run()


def test_type_not_in_numeric_expression() -> None:
    with pytest.raises(ParseError, match="nombre"):
        Interpreter("type(5) + 1;").run()
