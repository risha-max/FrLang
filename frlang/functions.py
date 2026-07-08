from __future__ import annotations

import copy
from dataclasses import dataclass

from frlang.lexer import Token
from frlang.types import TypeSpec, Value, NOTHING
from frlang.variables import Variable


@dataclass(frozen=True, slots=True)
class Parameter:
    name: str
    var_type: TypeSpec


@dataclass
class UserFunction:
    name: str
    params: list[Parameter]
    return_type: TypeSpec | None
    body_tokens: list[Token]
    line: int
    column: int


def copy_value(value: Value) -> Value:
    if value is NOTHING:
        return NOTHING
    if isinstance(value, list):
        return list(value)
    if isinstance(value, (int, float, str, bool)):
        return value
    return copy.deepcopy(value)
