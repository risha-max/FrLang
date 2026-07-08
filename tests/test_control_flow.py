import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def test_si_sinon() -> None:
    result = Interpreter(
        "si 2 < 1 { soit nombre x = 1; } sinon { soit nombre x = 2; } x;"
    ).run()
    assert result == 2


def test_si_sinon_si() -> None:
    result = Interpreter(
        "soit nombre x = 0; "
        "si x == 1 { x = 1; } sinon si x == 0 { x = 2; } sinon { x = 3; } "
        "x;"
    ).run()
    assert result == 2


def test_sinon_dans_pourchaque() -> None:
    interpreter = Interpreter(
        """
        pourchaque i dans range(1, 4) {
            si i mod 2 == 0 {
                afficher i;
            } sinon {
                afficher 0;
            }
        }
        """
    )
    interpreter.run()
    assert interpreter.output == ["0", "2", "0"]


def test_sinon_dans_tantque() -> None:
    interpreter = Interpreter(
        """
        soit nombre i = 0;
        tantque i < 3 {
            si i == 1 {
                afficher 10;
            } sinon {
                afficher i;
            }
            i = i + 1;
        }
        """
    )
    interpreter.run()
    assert interpreter.output == ["0", "10", "2"]


def test_arithmetique_dans_argument_methode() -> None:
    interpreter = Interpreter(
        """
        soit File file = nouveau File();
        soit nombre d = 1;
        file.enfiler(d + 1);
        afficher file.defiler();
        """
    )
    interpreter.run()
    assert interpreter.output == ["2"]


def test_tantque_avec_taille() -> None:
    interpreter = Interpreter(
        """
        soit File file = nouveau File();
        file.enfiler(1);
        file.enfiler(2);
        tantque file.taille() > 0 {
            afficher file.defiler();
        }
        """
    )
    interpreter.run()
    assert interpreter.output == ["1", "2"]


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
