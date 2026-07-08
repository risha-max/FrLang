import math

import pytest

from frlang.errors import LexerError, ParseError
from frlang.interpreter import Interpreter


def test_import_math_constants() -> None:
    result = Interpreter(
        """
        import Math;
        afficher Math.pi;
        afficher Math.e;
        afficher Math.phi;
        """
    ).run()
    assert result is None
    interpreter = Interpreter(
        """
        import Math;
        afficher Math.pi;
        """
    )
    interpreter.run()
    assert float(interpreter.output[0]) == pytest.approx(math.pi)


def test_math_factorielle() -> None:
    assert (
        Interpreter(
            """
            import Math;
            Math.factorielle(5);
            """
        ).run()
        == 120
    )


def test_math_factorielle_negative() -> None:
    with pytest.raises(ParseError, match="n'accepte pas les nombres négatifs"):
        Interpreter(
            """
            import Math;
            soit nombre n = 0 - 1;
            Math.factorielle(n);
            """
        ).run()


def test_from_math_import() -> None:
    assert Interpreter("from Math import factorielle; factorielle(4);").run() == 24


def test_math_random_bounds() -> None:
    for _ in range(20):
        value = Interpreter(
            """
            import Math;
            Math.random(1, 6);
            """
        ).run()
        assert isinstance(value, int)
        assert 1 <= value <= 6


def test_math_random_zero_args() -> None:
    value = Interpreter("import Math; Math.random();").run()
    assert isinstance(value, float)
    assert 0.0 <= value < 1.0
