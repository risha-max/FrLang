import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def test_mots_string_literal() -> None:
    interpreter = Interpreter(
        """
        soit Mots salut = "bonjour";
        afficher salut;
        """
    )
    interpreter.run()
    assert interpreter.output == ["bonjour"]


def test_rangee_brace_literal() -> None:
    interpreter = Interpreter(
        """
        soit Rangee notes = {10, 20, 30};
        afficher notes;
        """
    )
    interpreter.run()
    assert interpreter.output == ["Rangee [10, 20, 30]"]


def test_carnet_json_literal() -> None:
    interpreter = Interpreter(
        """
        soit Carnet eleve = {"nom": "Léa", "score": 10};
        afficher eleve.element("nom");
        afficher eleve.element("score");
        """
    )
    interpreter.run()
    assert interpreter.output == ["Léa", "10"]


def test_carnet_identifier_keys_literal() -> None:
    interpreter = Interpreter(
        """
        soit Carnet config = {actif: vrai, seuil: 42};
        afficher config.element("actif");
        afficher config.element("seuil");
        """
    )
    interpreter.run()
    assert interpreter.output == ["vrai", "42"]


def test_empty_rangee_literal() -> None:
    interpreter = Interpreter(
        """
        soit Rangee vide = {};
        afficher vide.taille();
        """
    )
    interpreter.run()
    assert interpreter.output == ["0"]


def test_nouveau_still_works() -> None:
    interpreter = Interpreter(
        """
        soit Rangee notes = nouveau Rangee(1, 2);
        soit Mots msg = nouveau Mots("salut");
        afficher notes;
        afficher msg;
        """
    )
    interpreter.run()
    assert interpreter.output == ["Rangee [1, 2]", "salut"]


def test_deprecated_bracket_literal_still_rejected() -> None:
    with pytest.raises(ParseError, match="ne crée plus"):
        Interpreter("soit Rangee r = Rangee [1];").run()


def test_carnet_literal_requires_colon() -> None:
    with pytest.raises(ParseError, match="il faut « : »"):
        Interpreter('soit Carnet c = {"nom" "Léa"};').run()
