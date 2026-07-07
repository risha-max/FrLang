import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def test_function_with_return() -> None:
    result = Interpreter(
        "definir fonction double(nombre n) { retourne n * 2; } retourne nombre double(5);"
    ).run()
    assert result == 10


def test_void_function_afficher() -> None:
    interpreter = Interpreter('definir fonction dire(Mots nom) { afficher nom; } dire("Salut");')
    interpreter.run()
    assert interpreter.output == ["Salut"]


def test_pass_by_value_primitive() -> None:
    result = Interpreter(
        "definir fonction essayer(nombre n) { n = n + 10; } "
        "soit nombre x = 5; essayer(x); x;"
    ).run()
    assert result == 5


def test_pass_by_pointer_primitive() -> None:
    result = Interpreter(
        "definir fonction incrementer(pointeur nombre p) { valeur(p) = valeur(p) + 1; } "
        "soit nombre x = 5; incrementer(adresse(x)); x;"
    ).run()
    assert result == 6


def test_pass_by_value_object() -> None:
    result = Interpreter(
        "definir fonction essayer(Sac s) { s.ajouter(99); } "
        "soit Sac boite = nouveau Sac(1); essayer(boite); boite.taille();"
    ).run()
    assert result == 1


def test_pass_by_pointer_object() -> None:
    result = Interpreter(
        "definir fonction remplir(pointeur Sac p) { valeur(p).ajouter(99); } "
        "soit Sac boite = nouveau Sac(1); remplir(adresse(boite)); boite.taille();"
    ).run()
    assert result == 2


def test_function_call_in_expression() -> None:
    result = Interpreter(
        "definir fonction double(nombre n) { retourne n * 2; } retourne nombre double(3) + 4;"
    ).run()
    assert result == 10


def test_undefined_function() -> None:
    with pytest.raises(ParseError, match="Je ne connais pas la fonction"):
        Interpreter("inconnue(1);").run()


def test_wrong_argument_count() -> None:
    with pytest.raises(ParseError, match="veut 1 valeur"):
        Interpreter(
            "definir fonction double(nombre n) { retourne n * 2; } retourne nombre double(1, 2);"
        ).run()


def test_return_in_void_function() -> None:
    with pytest.raises(ParseError, match="ne retourne rien"):
        Interpreter("definir fonction dire() { retourne 1; } dire();").run()


def test_missing_return() -> None:
    with pytest.raises(ParseError, match="doit retourner"):
        Interpreter(
            "definir fonction double(nombre n) { n = n + 1; } retourne nombre double(5);"
        ).run()


def test_function_already_defined() -> None:
    with pytest.raises(ParseError, match="existe déjà"):
        Interpreter(
            "definir fonction double(nombre n) { retourne n; } retourne nombre "
            "definir fonction double(nombre n) { retourne n; } retourne nombre"
        ).run()


def test_assignment_in_function_requires_existing() -> None:
    with pytest.raises(ParseError, match="Je ne connais pas"):
        Interpreter("definir fonction essayer() { x = 1; } essayer();").run()
