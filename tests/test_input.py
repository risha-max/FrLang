import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def test_demander_without_prompt() -> None:
    interpreter = Interpreter(
        """
        soit Mots nom = demander();
        afficher nom;
        """,
        input_lines=["Alice"],
    )
    interpreter.run()
    assert interpreter.output == ["Alice"]


def test_demander_with_prompt() -> None:
    interpreter = Interpreter(
        """
        soit Mots nom = demander("Nom : ");
        afficher nom;
        """,
        input_lines=["Bob"],
    )
    interpreter.run()
    assert interpreter.output == ["Nom : ", "Bob"]


def test_lire_number() -> None:
    assert (
        Interpreter(
            "soit nombre age = lire(); age;",
            input_lines=["12"],
        ).run()
        == 12
    )


def test_lire_float() -> None:
    assert (
        Interpreter(
            "lire();",
            input_lines=["3.5"],
        ).run()
        == 3.5
    )


def test_lire_empty_line() -> None:
    with pytest.raises(ParseError, match="ligne vide"):
        Interpreter("lire();", input_lines=[""]).run()


def test_lire_invalid_number() -> None:
    with pytest.raises(ParseError, match="n'est pas un nombre valide"):
        Interpreter("lire();", input_lines=["abc"]).run()


def test_input_eof() -> None:
    with pytest.raises(ParseError, match="Plus aucune entrée"):
        Interpreter("demander();", input_lines=[]).run()
