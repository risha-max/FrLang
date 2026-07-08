class FrLangError(Exception):
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


class LexerError(FrLangError):
    """Erreur de lecture du code."""


class ParseError(FrLangError):
    """Erreur dans la façon dont le calcul est écrit."""


class ReturnSignal(Exception):
    """Fin anticipée d'une fonction (retourne)."""

    def __init__(self, value: object | None) -> None:
        self.value = value


class BreakSignal(Exception):
    """Sortie anticipée d'une boucle (arreter)."""


class ContinueSignal(Exception):
    """Passe à l'itération suivante d'une boucle (continuer)."""
