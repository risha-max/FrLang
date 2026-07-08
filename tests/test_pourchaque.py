import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def test_pourchaque_range_single_arg() -> None:
    interpreter = Interpreter(
        """
        soit nombre somme = 0;
        pourchaque i dans range(5) {
            somme = somme + i;
        }
        somme;
        """
    )
    assert interpreter.run() == 10


def test_pourchaque_range_two_args() -> None:
    interpreter = Interpreter(
        """
        soit Rangee resultat = nouveau Rangee();
        pourchaque n dans range(2, 5) {
            resultat.ajouter(n);
        }
        afficher resultat;
        """
    )
    interpreter.run()
    assert interpreter.output == ["Rangee [2, 3, 4]"]


def test_pourchaque_range_step() -> None:
    interpreter = Interpreter(
        """
        soit Rangee resultat = nouveau Rangee();
        pourchaque n dans range(0, 10, 2) {
            resultat.ajouter(n);
        }
        afficher resultat;
        """
    )
    interpreter.run()
    assert interpreter.output == ["Rangee [0, 2, 4, 6, 8]"]


def test_pourchaque_range_negative_step() -> None:
    result = Interpreter(
        """
        soit nombre compte = 0;
        pourchaque i dans range(3, 0, -1) {
            compte = compte + 1;
        }
        compte;
        """
    ).run()
    assert result == 3


def test_pourchaque_over_rangee() -> None:
    interpreter = Interpreter(
        """
        soit Rangee notes = nouveau Rangee(10, 20, 30);
        soit nombre somme = 0;
        pourchaque note dans notes {
            somme = somme + note;
        }
        somme;
        """
    )
    assert interpreter.run() == 60


def test_pourchaque_over_sac() -> None:
    interpreter = Interpreter(
        """
        soit Sac fruits = nouveau Sac("pomme", "poire");
        soit nombre compte = 0;
        pourchaque fruit dans fruits {
            compte = compte + 1;
        }
        compte;
        """
    )
    assert interpreter.run() == 2


def test_range_builtin_expression() -> None:
    interpreter = Interpreter("afficher range(4).taille();")
    interpreter.run()
    assert interpreter.output == ["4"]


def test_pourchaque_rejects_non_collection() -> None:
    with pytest.raises(ParseError, match="il faut une Collection"):
        Interpreter(
            """
            soit nombre x = 5;
            pourchaque i dans x {
                afficher i;
            }
            """
        ).run()


def test_pourchaque_requires_dans() -> None:
    with pytest.raises(ParseError, match="il faut écrire dans"):
        Interpreter("pourchaque i { afficher i; }").run()
