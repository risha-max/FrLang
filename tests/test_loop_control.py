import pytest

from frlang.errors import ParseError
from frlang.interpreter import Interpreter


def test_arreter_in_pourchaque() -> None:
    interpreter = Interpreter(
        """
        pourchaque i dans range(10) {
            si i == 3 {
                arreter;
            }
            afficher i;
        }
        """
    )
    interpreter.run()
    assert interpreter.output == ["0", "1", "2"]


def test_continuer_in_pourchaque() -> None:
    interpreter = Interpreter(
        """
        pourchaque i dans range(5) {
            si i mod 2 == 0 {
                continuer;
            }
            afficher i;
        }
        """
    )
    interpreter.run()
    assert interpreter.output == ["1", "3"]


def test_arreter_outside_loop() -> None:
    with pytest.raises(ParseError, match="dans une boucle"):
        Interpreter("arreter;").run()
