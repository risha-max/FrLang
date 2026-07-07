from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterator

from sac.messages import incomplete_number, invalid_number, unterminated_text, unknown_symbol, unknown_word

_KEYWORDS: dict[str, "TokenKind"] = {}


class TokenKind(Enum):
    NUMBER = auto()
    TEXT = auto()
    VRAI = auto()
    FAUX = auto()
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
    RETOURNE = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()


_KEYWORDS.update(
    {
        "mod": TokenKind.MOD,
        "soit": TokenKind.SOIT,
        "afficher": TokenKind.AFFICHER,
        "definir": TokenKind.DEFINIR,
        "retourne": TokenKind.RETOURNE,
        "pointeur": TokenKind.TYPE,
        "nombre": TokenKind.TYPE,
        "mots": TokenKind.TYPE,
        "logique": TokenKind.TYPE,
        "rangée": TokenKind.TYPE,
        "sac": TokenKind.TYPE,
        "carnet": TokenKind.TYPE,
        "tas": TokenKind.TYPE,
        "file": TokenKind.TYPE,
        "vrai": TokenKind.VRAI,
        "faux": TokenKind.FAUX,
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
                    yield Token(TokenKind.EQUAL, "=", start_line, start_column)
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
        if word in {"entier", "reel", "vrai_faux", "booleen", "bool"}:
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
