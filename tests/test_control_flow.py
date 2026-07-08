import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def test_si_sinon() -> None:
    result = Interpreter(
        "si 2 < 1 { soit nombre x = 1; } sinon { soit nombre x = 2; } x;"
    ).run()
    assert result == 2


def test_tantque_while_loop() -> None:
    result = Interpreter(
        "soit nombre i = 0; "
        "soit nombre somme = 0; "
        "tantque i < 5 { somme = somme + i; i = i + 1; } "
        "somme;"
    ).run()
    assert result == 10


def test_deprecated_tant_keyword() -> None:
    from frlang.errors import LexerError
    from frlang.lexer import Lexer

    with pytest.raises(LexerError, match="Écris plutôt tantque"):
        Lexer("tant").tokenize()


def test_comparisons() -> None:
    interpreter = Interpreter("si 3 > 2 { afficher vrai; }")
    interpreter.run()
    assert interpreter.output == ["vrai"]


def test_return_inside_si() -> None:
    result = Interpreter(
        "definir fonction signe(nombre n) { "
        "si n < 0 { retourne -1; } "
        "si n == 0 { retourne 0; } "
        "retourne 1; "
        "} retourne nombre signe(-4);"
    ).run()
    assert result == -1


def test_return_outside_function() -> None:
    with pytest.raises(ParseError, match="ne peut être utilisé que dans une fonction"):
        Interpreter("retourne 1;").run()


def test_n_premiers_primes_program() -> None:
    from pathlib import Path

    source = Path("probleme/n_premiers_primes").read_text(encoding="utf-8")
    interpreter = Interpreter(source)
    interpreter.run()
    assert interpreter.output == ["Rangee [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]"]
