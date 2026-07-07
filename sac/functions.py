from __future__ import annotations

import copy
from dataclasses import dataclass

from sac.types import TypeSpec, Value
from sac.variables import Variable


@dataclass(frozen=True, slots=True)
class Parameter:
    name: str
    var_type: TypeSpec


@dataclass
class UserFunction:
    name: str
    params: list[Parameter]
    return_type: TypeSpec | None
    body_start: int
    body_end: int
    line: int
    column: int


def copy_value(value: Value) -> Value:
    if isinstance(value, (int, float, str, bool)):
        return value
    return copy.deepcopy(value)
