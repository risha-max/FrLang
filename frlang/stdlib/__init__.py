from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from frlang.imports import LoadedModule, NativeFunction
from frlang.types import Value

if TYPE_CHECKING:
    from frlang.interpreter import Interpreter

BuiltinFactory = Callable[[], LoadedModule]

_BUILTIN_FACTORIES: dict[str, BuiltinFactory] = {}


def register_builtin_module(name: str, factory: BuiltinFactory) -> None:
    _BUILTIN_FACTORIES[name] = factory


def builtin_module_path(name: str) -> Path:
    return Path(f"<builtin:{name}>")


def get_builtin_module(name: str) -> LoadedModule | None:
    factory = _BUILTIN_FACTORIES.get(name)
    if factory is None:
        return None
    return factory()


def call_native_function(
    interpreter: Interpreter,
    spec: NativeFunction,
    args: list[Value],
    line: int,
    column: int,
) -> Value:
    if len(args) < spec.min_args or len(args) > spec.max_args:
        from frlang.messages import native_wrong_argument_count

        if spec.min_args == spec.max_args:
            expected = f"{spec.min_args} argument(s)"
        else:
            expected = f"entre {spec.min_args} et {spec.max_args} arguments"
        raise native_wrong_argument_count(spec.name, expected, len(args), line, column)
    return spec.handler(interpreter, args, line, column)


def _register_defaults() -> None:
    from frlang.stdlib.math_module import create_math_module

    register_builtin_module("Math", create_math_module)


_register_defaults()
