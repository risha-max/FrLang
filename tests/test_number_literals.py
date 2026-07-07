import pytest

from frlang.errors import LexerError
from frlang.interpreter import Interpreter


def evaluate(source: str) -> float | int:
    value = Interpreter(source).run()
    assert value is not None
    return value  # type: ignore[return-value]


def test_binary_literal() -> None:
    assert evaluate("soit nombre x = b'10101010'; x;") == 170


def test_hex_literal() -> None:
    assert evaluate("soit nombre x = h'10471284'; x;") == 0x10471284


def test_hex_literal_lowercase() -> None:
    assert evaluate("soit nombre x = h'1a2b'; x;") == 0x1A2B


def test_binary_in_expression() -> None:
    assert evaluate("b'1010' + 6;") == 16


def test_unknown_prefix() -> None:
    with pytest.raises(LexerError, match="Je ne connais pas « c'"):
        Interpreter("soit nombre x = c'klfsjfskljfsd';").run()


def test_invalid_binary_characters() -> None:
    with pytest.raises(LexerError, match="nombre binaire est mal écrit"):
        Interpreter("soit nombre x = b'lkfjflksjf;sjfsda';").run()


def test_invalid_hex_characters() -> None:
    with pytest.raises(LexerError, match="nombre hexadécimal est mal écrit"):
        Interpreter("soit nombre x = h'sfksjdfksjfs';").run()


def test_empty_binary_literal() -> None:
    with pytest.raises(LexerError, match="Il manque des chiffres"):
        Interpreter("soit nombre x = b'';").run()


def test_unterminated_binary_literal() -> None:
    with pytest.raises(LexerError, match="Il manque une apostrophe"):
        Interpreter("soit nombre x = b'1010;").run()
