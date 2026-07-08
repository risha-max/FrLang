from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from frlang.classes import ClassDef
from frlang.functions import UserFunction
from frlang.objects import FrLangObject
from frlang.types import Value
from frlang.variables import Variable

if TYPE_CHECKING:
    from frlang.interpreter import Interpreter

NativeHandler = Callable[["Interpreter", list[Value], int, int], Value]


@dataclass(frozen=True, slots=True)
class NativeFunction:
    name: str
    min_args: int
    max_args: int
    handler: NativeHandler


@dataclass
class LoadedModule:
    name: str
    path: Path
    functions: dict[str, UserFunction] = field(default_factory=dict)
    classes: dict[str, ClassDef] = field(default_factory=dict)
    variables: dict[str, Variable] = field(default_factory=dict)
    native_functions: dict[str, NativeFunction] = field(default_factory=dict)


class ModuleNamespace(FrLangObject):
    __slots__ = ("module_name", "module", "_interpreter")

    def __init__(self, interpreter: object, module: LoadedModule) -> None:
        self._interpreter = interpreter
        self.module_name = module.name
        self.module = module

    @property
    def type_name(self) -> str:
        return "Module"

    def describe(self) -> str:
        return f"Module({self.module_name})"

    def call_method(
        self,
        name: str,
        args: list[Value],
        line: int,
        column: int,
    ) -> Value | None:
        from frlang.messages import import_name_not_exported

        raise import_name_not_exported(self.module_name, name, line, column)


def resolve_module_path(module_name: str, source_path: Path | None) -> Path:
    candidate = Path(module_name)
    if candidate.is_file():
        return candidate.resolve()

    if source_path is not None:
        relative = (source_path.parent / module_name).resolve()
        if relative.is_file():
            return relative

    raise FileNotFoundError(module_name)
