import pytest

from frlang.errors import LexerError, ParseError
from frlang.interpreter import Interpreter


def test_line_comment_ignored() -> None:
    interpreter = Interpreter(
        """
        // commentaire complet
        soit nombre x = 1; // fin de ligne
        afficher x;
        """
    )
    interpreter.run()
    assert interpreter.output == ["1"]


def test_block_comment_ignored() -> None:
    interpreter = Interpreter(
        """
        /* début
           milieu */
        soit nombre x = 2;
        afficher x;
        """
    )
    interpreter.run()
    assert interpreter.output == ["2"]


def test_unterminated_block_comment() -> None:
    with pytest.raises(LexerError, match="jamais fermé"):
        Interpreter("/* oups").run()
