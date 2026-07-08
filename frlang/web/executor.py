from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from frlang.errors import FrLangError, LexerError, ParseError
from frlang.interpreter import Interpreter
from frlang.types import Value, format_value


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    ok: bool
    stdout: list[str]
    result: str | None
    error: str | None


def execute_source(source: str, source_path: Path) -> ExecutionResult:
    interpreter = Interpreter.session()
    interpreter._source_path = source_path.resolve()
    try:
        value = interpreter.execute(source)
    except (LexerError, ParseError, FrLangError) as error:
        return ExecutionResult(ok=False, stdout=[], result=None, error=str(error))

    return ExecutionResult(
        ok=True,
        stdout=list(interpreter.output),
        result=_format_result(value),
        error=None,
    )


def _format_result(value: Value | None) -> str | None:
    if value is None:
        return None
    return format_value(value)
