from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterator

from frlang.messages import (
    empty_based_literal,
    incomplete_number,
    invalid_binary_literal,
    invalid_hex_literal,
    invalid_number,
    unterminated_number_literal,
    unterminated_text,
    unknown_number_prefix,
    unknown_symbol,
    unknown_word,
)

_KEYWORDS: dict[str, "TokenKind"] = {}


class TokenKind(Enum):
    NUMBER = auto()
    TEXT = auto()
    VRAI = auto()
    FAUX = auto()
    RIEN = auto()
    IDENTIFIER = auto()
    SOIT = auto()
    AFFICHER = auto()
    TYPE = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    MOD = auto()
    CARET = auto()
    EQUAL = auto()
    SEMICOLON = auto()
    DOT = auto()
    COMMA = auto()
    COLON = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    DEFINIR = auto()
    FONCTION = auto()
    CLASSE = auto()
    HERITE = auto()
    DE = auto()
    RETOURNE = auto()
    NOUVEAU = auto()
    CONSTRUCTEUR = auto()
    SI = auto()
    SINON = auto()
    IMPORT = auto()
    FROM = auto()
    AS = auto()
    TANTQUE = auto()
    POURCHAQUE = auto()
    DANS = auto()
    EQEQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()


_KEYWORDS.update(
    {
        "mod": TokenKind.MOD,
        "soit": TokenKind.SOIT,
        "afficher": TokenKind.AFFICHER,
        "definir": TokenKind.DEFINIR,
        "fonction": TokenKind.FONCTION,
        "classe": TokenKind.CLASSE,
        "herite": TokenKind.HERITE,
        "de": TokenKind.DE,
        "retourne": TokenKind.RETOURNE,
        "nouveau": TokenKind.NOUVEAU,
        "constructeur": TokenKind.CONSTRUCTEUR,
        "si": TokenKind.SI,
        "sinon": TokenKind.SINON,
        "import": TokenKind.IMPORT,
        "from": TokenKind.FROM,
        "as": TokenKind.AS,
        "tantque": TokenKind.TANTQUE,
        "pourchaque": TokenKind.POURCHAQUE,
        "dans": TokenKind.DANS,
        "pointeur": TokenKind.TYPE,
        "nombre": TokenKind.TYPE,
        "Mots": TokenKind.TYPE,
        "logique": TokenKind.TYPE,
        "Rangee": TokenKind.TYPE,
        "Sac": TokenKind.TYPE,
        "Carnet": TokenKind.TYPE,
        "Tas": TokenKind.TYPE,
        "File": TokenKind.TYPE,
        "Fichier": TokenKind.TYPE,
        "Arbre": TokenKind.TYPE,
        "Graphe": TokenKind.TYPE,
        "vrai": TokenKind.VRAI,
        "faux": TokenKind.FAUX,
        "rien": TokenKind.RIEN,
    }
)


@dataclass(frozen=True, slots=True)
class Token:
    kind: TokenKind
    value: str | float | None
    line: int
    column: int


class Lexer:
    """Tokenise une expression ou un petit programme."""

    def __init__(self, source: str) -> None:
        self._source = source
        self._index = 0
        self._line = 1
        self._column = 1

    def tokenize(self) -> list[Token]:
        return list(self._scan_tokens())

    def _scan_tokens(self) -> Iterator[Token]:
        while self._index < len(self._source):
            char = self._source[self._index]

            if char.isspace():
                self._advance()
                continue

            if char.isdigit() or (char == "." and self._peek_next().isdigit()):
                yield self._read_number()
                continue

            if char == '"':
                yield self._read_text()
                continue

            if char.isalpha() or char == "_":
                if char.isalpha() and self._peek_next() == "'":
                    if char == "b":
                        yield self._read_based_number("binary")
                        continue
                    if char == "h":
                        yield self._read_based_number("hex")
                        continue
                    yield self._read_unknown_number_prefix()
                    continue
                yield self._read_word()
                continue

            start_line = self._line
            start_column = self._column
            self._advance()

            match char:
                case "+":
                    yield Token(TokenKind.PLUS, "+", start_line, start_column)
                case "-":
                    yield Token(TokenKind.MINUS, "-", start_line, start_column)
                case "*":
                    yield Token(TokenKind.STAR, "*", start_line, start_column)
                case "/":
                    yield Token(TokenKind.SLASH, "/", start_line, start_column)
                case "^":
                    yield Token(TokenKind.CARET, "^", start_line, start_column)
                case "=":
                    if self._peek_current() == "=":
                        self._advance()
                        yield Token(TokenKind.EQEQ, "==", start_line, start_column)
                    else:
                        yield Token(TokenKind.EQUAL, "=", start_line, start_column)
                case "!":
                    if self._peek_current() == "=":
                        self._advance()
                        yield Token(TokenKind.NEQ, "!=", start_line, start_column)
                    else:
                        raise unknown_symbol(char, start_line, start_column)
                case "<":
                    if self._peek_current() == "=":
                        self._advance()
                        yield Token(TokenKind.LTE, "<=", start_line, start_column)
                    else:
                        yield Token(TokenKind.LT, "<", start_line, start_column)
                case ">":
                    if self._peek_current() == "=":
                        self._advance()
                        yield Token(TokenKind.GTE, ">=", start_line, start_column)
                    else:
                        yield Token(TokenKind.GT, ">", start_line, start_column)
                case ";":
                    yield Token(TokenKind.SEMICOLON, ";", start_line, start_column)
                case ".":
                    yield Token(TokenKind.DOT, ".", start_line, start_column)
                case ",":
                    yield Token(TokenKind.COMMA, ",", start_line, start_column)
                case ":":
                    yield Token(TokenKind.COLON, ":", start_line, start_column)
                case "[":
                    yield Token(TokenKind.LBRACKET, "[", start_line, start_column)
                case "]":
                    yield Token(TokenKind.RBRACKET, "]", start_line, start_column)
                case "{":
                    yield Token(TokenKind.LBRACE, "{", start_line, start_column)
                case "}":
                    yield Token(TokenKind.RBRACE, "}", start_line, start_column)
                case "(":
                    yield Token(TokenKind.LPAREN, "(", start_line, start_column)
                case ")":
                    yield Token(TokenKind.RPAREN, ")", start_line, start_column)
                case _:
                    raise unknown_symbol(char, start_line, start_column)

        yield Token(TokenKind.EOF, None, self._line, self._column)

    def _read_word(self) -> Token:
        start_line = self._line
        start_column = self._column
        start = self._index

        while self._index < len(self._source) and (
            self._source[self._index].isalnum() or self._source[self._index] == "_"
        ):
            self._advance()

        word = self._source[start : self._index]
        if word in {"entier", "reel", "vrai_faux", "booleen", "bool", "tant"}:
            raise unknown_word(word, start_line, start_column)

        kind = _KEYWORDS.get(word, TokenKind.IDENTIFIER)
        return Token(kind, word, start_line, start_column)

    def _read_text(self) -> Token:
        start_line = self._line
        start_column = self._column
        self._advance()

        chars: list[str] = []
        while self._index < len(self._source) and self._source[self._index] != '"':
            char = self._source[self._index]
            if char == "\n":
                raise unterminated_text(start_line, start_column)
            if char == "\\":
                self._advance()
                if self._index >= len(self._source):
                    raise unterminated_text(start_line, start_column)
                escape = self._source[self._index]
                chars.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(escape, escape))
                self._advance()
                continue
            chars.append(char)
            self._advance()

        if self._index >= len(self._source):
            raise unterminated_text(start_line, start_column)

        self._advance()
        return Token(TokenKind.TEXT, "".join(chars), start_line, start_column)

    def _read_number(self) -> Token:
        start_line = self._line
        start_column = self._column
        start = self._index

        while self._index < len(self._source) and self._source[self._index].isdigit():
            self._advance()

        if self._index < len(self._source) and self._source[self._index] == ".":
            self._advance()
            while self._index < len(self._source) and self._source[self._index].isdigit():
                self._advance()

        raw = self._source[start:self._index]
        if raw == ".":
            raise incomplete_number(start_line, start_column)

        try:
            value: float = float(raw) if "." in raw else int(raw)
        except ValueError as exc:
            raise invalid_number(raw, start_line, start_column) from exc

        return Token(TokenKind.NUMBER, value, start_line, start_column)

    def _read_based_number(self, base: str) -> Token:
        start_line = self._line
        start_column = self._column
        self._advance()

        if self._is_at_end() or self._source[self._index] != "'":
            raise unknown_number_prefix(self._source[start_column - 1], start_line, start_column)

        self._advance()
        content_start = self._index

        while self._index < len(self._source) and self._source[self._index] != "'":
            if self._source[self._index] == "\n":
                raise unterminated_number_literal(base, start_line, start_column)
            self._advance()

        if self._index >= len(self._source):
            raise unterminated_number_literal(base, start_line, start_column)

        content = self._source[content_start : self._index]
        self._advance()

        if not content:
            raise empty_based_literal(base, start_line, start_column)

        if base == "binary":
            if any(char not in "01" for char in content):
                raise invalid_binary_literal(content, start_line, start_column)
            value = int(content, 2)
        else:
            if any(char not in "0123456789abcdefABCDEF" for char in content):
                raise invalid_hex_literal(content, start_line, start_column)
            value = int(content, 16)

        return Token(TokenKind.NUMBER, value, start_line, start_column)

    def _read_unknown_number_prefix(self) -> Token:
        start_line = self._line
        start_column = self._column
        prefix = self._advance()
        self._advance()

        while self._index < len(self._source) and self._source[self._index] != "'":
            if self._source[self._index] == "\n":
                raise unterminated_number_literal(prefix, start_line, start_column)
            self._advance()

        if self._index >= len(self._source):
            raise unterminated_number_literal(prefix, start_line, start_column)

        self._advance()
        raise unknown_number_prefix(prefix, start_line, start_column)

    def _is_at_end(self) -> bool:
        return self._index >= len(self._source)

    def _peek_current(self) -> str:
        if self._is_at_end():
            return ""
        return self._source[self._index]

    def _peek_next(self) -> str:
        if self._index + 1 >= len(self._source):
            return ""
        return self._source[self._index + 1]

    def _advance(self) -> str:
        char = self._source[self._index]
        self._index += 1
        if char == "\n":
            self._line += 1
            self._column = 1
        else:
            self._column += 1
        return char
