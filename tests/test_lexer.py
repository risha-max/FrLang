import pytest

from frlang.errors import LexerError, ParseError
from frlang.interpreter import Interpreter
from frlang.lexer import Lexer, TokenKind


def kinds(source: str) -> list[TokenKind]:
    return [token.kind for token in Lexer(source).tokenize()]


def run(source: str) -> tuple[object | None, list[str]]:
    interpreter = Interpreter(source)
    return interpreter.run(), interpreter.output


def evaluate(source: str) -> float | int:
    value, _ = run(source)
    assert value is not None
    return value  # type: ignore[return-value]


def test_typed_declaration_tokens() -> None:
    assert kinds("soit nombre x = 5;") == [
        TokenKind.SOIT,
        TokenKind.TYPE,
        TokenKind.IDENTIFIER,
        TokenKind.EQUAL,
        TokenKind.NUMBER,
        TokenKind.SEMICOLON,
        TokenKind.EOF,
    ]


def test_logique_literal_tokens() -> None:
    assert kinds("vrai") == [TokenKind.VRAI, TokenKind.EOF]
    assert kinds("faux") == [TokenKind.FAUX, TokenKind.EOF]


def test_addition_and_precedence() -> None:
    assert evaluate("2 + 3 * 4") == 14


def test_variable_declaration_and_use() -> None:
    value, output = run("soit nombre a = 5; soit nombre b = a + 3; b;")
    assert value == 8
    assert output == []


def test_afficher_inline_declaration() -> None:
    value, output = run("afficher soit nombre x = 5;")
    assert value is None
    assert output == ["5"]


def test_afficher_variable() -> None:
    value, output = run("soit nombre x = 5; afficher x;")
    assert value is None
    assert output == ["5"]


def test_nombre_accepts_integer() -> None:
    value, _ = run("soit nombre age = 12; age;")
    assert value == 12


def test_nombre_accepts_decimal() -> None:
    value, _ = run("soit nombre pi = 3.14; pi;")
    assert value == 3.14


def test_mots_type() -> None:
    value, _ = run('soit Mots ville = "Montréal"; ville;')
    assert value.text == "Montréal"


def test_logique_type() -> None:
    value, _ = run("soit logique actif = vrai; actif;")
    assert value is True


def test_afficher_logique() -> None:
    _, output = run("soit logique ok = faux; afficher ok;")
    assert output == ["faux"]


def test_mots_rejects_number() -> None:
    with pytest.raises(ParseError, match="il faut un Mots"):
        run("soit Mots x = 5;")


def test_logique_rejects_number() -> None:
    with pytest.raises(ParseError, match="il faut un logique"):
        run("soit logique x = 5;")


def test_logique_in_numeric_expression() -> None:
    with pytest.raises(ParseError, match="ne peut pas faire de calcul avec un logique"):
        run("soit logique actif = vrai; actif + 1;")


def test_deprecated_entier_type() -> None:
    with pytest.raises(LexerError, match="Écris plutôt nombre"):
        Lexer("entier").tokenize()


def test_deprecated_reel_type() -> None:
    with pytest.raises(LexerError, match="Écris plutôt nombre"):
        Lexer("reel").tokenize()


def test_deprecated_vrai_faux_type() -> None:
    with pytest.raises(LexerError, match="Écris plutôt logique"):
        Lexer("vrai_faux").tokenize()


def test_duplicate_same_type() -> None:
    with pytest.raises(ParseError, match="déjà créé « x »"):
        run("soit nombre x = 5; soit nombre x = 10;")


def test_duplicate_different_type() -> None:
    with pytest.raises(ParseError, match="existe déjà"):
        run('soit nombre x = 5; soit Mots x = "hi";')


def test_type_used_as_variable_name() -> None:
    with pytest.raises(ParseError, match="mot spécial, pas un nom"):
        run("soit nombre nombre = 5;")


def test_type_used_in_expression() -> None:
    with pytest.raises(ParseError, match="mot spécial, pas un nom à utiliser"):
        run("soit nombre x = 5; nombre + 1;")


def test_missing_type_before_name() -> None:
    with pytest.raises(ParseError, match="il manque la sorte"):
        run("soit x = 5;")
