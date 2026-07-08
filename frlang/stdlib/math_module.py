from __future__ import annotations

import math
import random as py_random

from frlang.imports import LoadedModule, NativeFunction
from frlang.stdlib import builtin_module_path
from frlang.types import VarType
from frlang.variables import Variable


def _as_int(value: object, name: str, line: int, column: int) -> int:
    from frlang.messages import math_requires_integer

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise math_requires_integer(name, line, column)
    if isinstance(value, float) and not value.is_integer():
        raise math_requires_integer(name, line, column)
    return int(value)


def _factorielle(_interpreter: object, args: list[object], line: int, column: int) -> int:
    from frlang.messages import factorial_negative

    n = _as_int(args[0], "n", line, column)
    if n < 0:
        raise factorial_negative(line, column)
    return math.factorial(n)


def _random(_interpreter: object, args: list[object], line: int, column: int) -> int | float:
    from frlang.messages import random_invalid_range

    if len(args) == 0:
        return py_random.random()
    if len(args) == 1:
        upper = _as_int(args[0], "max", line, column)
        if upper <= 0:
            raise random_invalid_range(line, column)
        return py_random.randrange(upper)
    low = _as_int(args[0], "min", line, column)
    high = _as_int(args[1], "max", line, column)
    if low > high:
        raise random_invalid_range(line, column)
    return py_random.randint(low, high)


def create_math_module() -> LoadedModule:
    phi = (1 + math.sqrt(5)) / 2
    return LoadedModule(
        name="Math",
        path=builtin_module_path("Math"),
        variables={
            "pi": Variable(VarType.NOMBRE, math.pi),
            "e": Variable(VarType.NOMBRE, math.e),
            "phi": Variable(VarType.NOMBRE, phi),
        },
        native_functions={
            "factorielle": NativeFunction(
                name="factorielle",
                min_args=1,
                max_args=1,
                handler=_factorielle,
            ),
            "random": NativeFunction(
                name="random",
                min_args=0,
                max_args=2,
                handler=_random,
            ),
        },
    )
