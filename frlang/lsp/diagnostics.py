from __future__ import annotations

from dataclasses import dataclass

from frlang.errors import FrLangError, LexerError
from frlang.interpreter import Interpreter


@dataclass(frozen=True, slots=True)
class DiagnosticMessage:
    line: int
    column: int
    message: str
    hint: str | None = None


def analyze_source(source: str) -> list[DiagnosticMessage]:
    if not source.strip():
        return []

    try:
        Interpreter(source).run()
    except (LexerError, FrLangError) as error:
        return [
            DiagnosticMessage(
                line=error.line,
                column=error.column,
                message=error.message,
                hint=error.hint,
            )
        ]
    return []
