import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def test_primitive_defaults_without_initializer() -> None:
    interpreter = Interpreter(
        """
        soit nombre x;
        soit logique ok;
        soit pointeur nombre p;
        afficher x;
        afficher ok;
        afficher p;
        """
    )
    interpreter.run()
    assert interpreter.output == ["rien", "rien", "rien"]


def test_explicit_rien_initializer() -> None:
    interpreter = Interpreter(
        """
        soit nombre x = rien;
        soit logique ok = rien;
        soit pointeur nombre p = rien;
        afficher x;
        """
    )
    interpreter.run()
    assert interpreter.output == ["rien"]


def test_rien_not_allowed_for_mots() -> None:
    with pytest.raises(ParseError, match="ne convient pas"):
        Interpreter('soit Mots nom = rien;').run()


def test_class_field_defaults() -> None:
    interpreter = Interpreter(
        """
        definir classe Boite {
            soit nombre compte;
            soit logique actif;
            soit pointeur nombre lien;
        }
        soit Boite b = nouveau Boite();
        afficher b.compte;
        afficher b.actif;
        afficher b.lien;
        """
    )
    interpreter.run()
    assert interpreter.output == ["rien", "rien", "rien"]


def test_nothing_cannot_be_used_in_math() -> None:
    with pytest.raises(ParseError, match="vaut rien"):
        Interpreter("soit nombre x; x + 1;").run()
