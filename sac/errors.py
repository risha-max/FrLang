class SacError(Exception):
    """Erreur de base du langage."""

    def __init__(
        self,
        message: str,
        *,
        line: int = 1,
        column: int = 1,
        hint: str | None = None,
    ) -> None:
        self.line = line
        self.column = column
        self.message = message
        self.hint = hint

        text = f"Ligne {line} : {message}"
        if hint:
            text += f"\n\nAstuce : {hint}"
        super().__init__(text)


class LexerError(SacError):
    """Erreur de lecture du code."""


class ParseError(SacError):
    """Erreur dans la façon dont le calcul est écrit."""
