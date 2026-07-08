from __future__ import annotations

import copy
from dataclasses import dataclass

from frlang.memory import is_primitive_array
from frlang.lexer import Token
from frlang.types import NOTHING, TypeSpec, Value
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
    if is_primitive_array(value):
        return value.copy()
    if isinstance(value, list):
        return list(value)
    if isinstance(value, (int, float, str, bool)):
        return value
    return copy.deepcopy(value)
