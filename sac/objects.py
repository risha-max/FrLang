from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from sac.messages import (
    carnet_key_missing,
    empty_collection,
    index_out_of_range,
    sac_no_order_access,
    unknown_object_method,
    wrong_method_argument_count,
)
from sac.types import Value, format_value


class ObjetSac(ABC):
    @property
    @abstractmethod
    def type_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def call_method(
        self,
        name: str,
        args: list[Value],
        line: int,
        column: int,
    ) -> Value | None:
        raise NotImplementedError

    @abstractmethod
    def describe(self) -> str:
        raise NotImplementedError


def _expect_count(
    method: str,
    args: list[Value],
    expected: int,
    line: int,
    column: int,
) -> None:
    if len(args) != expected:
        raise wrong_method_argument_count(method, expected, len(args), line, column)


@dataclass
class Rangee(ObjetSac):
    items: list[Value] = field(default_factory=list)

    @property
    def type_name(self) -> str:
        return "rangée"

    def describe(self) -> str:
        inner = ", ".join(format_value(item) for item in self.items)
        return f"rangée [{inner}]"

    def call_method(
        self,
        name: str,
        args: list[Value],
        line: int,
        column: int,
    ) -> Value | None:
        match name:
            case "ajouter":
                _expect_count(name, args, 1, line, column)
                self.items.append(args[0])
                return None
            case "element":
                _expect_count(name, args, 1, line, column)
                return self._element(args[0], line, column)
            case "premier":
                _expect_count(name, args, 0, line, column)
                return self._element(1, line, column)
            case "dernier":
                _expect_count(name, args, 0, line, column)
                return self._element(len(self.items), line, column)
            case "taille":
                _expect_count(name, args, 0, line, column)
                return len(self.items)
            case "contient":
                _expect_count(name, args, 1, line, column)
                return args[0] in self.items
            case "vider":
                _expect_count(name, args, 0, line, column)
                self.items.clear()
                return None
            case _:
                raise unknown_object_method(self.type_name, name, line, column)

    def _element(self, position: Value, line: int, column: int) -> Value:
        if isinstance(position, bool) or not isinstance(position, (int, float)):
            raise index_out_of_range(self.type_name, position, len(self.items), line, column)
        index = int(position)
        if index < 1 or index > len(self.items):
            raise index_out_of_range(self.type_name, index, len(self.items), line, column)
        return self.items[index - 1]


@dataclass
class Sac(ObjetSac):
    items: list[Value] = field(default_factory=list)

    @property
    def type_name(self) -> str:
        return "sac"

    def describe(self) -> str:
        inner = ", ".join(format_value(item) for item in self.items)
        return f"sac [{inner}]"

    def call_method(
        self,
        name: str,
        args: list[Value],
        line: int,
        column: int,
    ) -> Value | None:
        match name:
            case "ajouter":
                _expect_count(name, args, 1, line, column)
                if args[0] not in self.items:
                    self.items.append(args[0])
                return None
            case "retirer":
                _expect_count(name, args, 1, line, column)
                if args[0] in self.items:
                    self.items.remove(args[0])
                return None
            case "taille":
                _expect_count(name, args, 0, line, column)
                return len(self.items)
            case "contient":
                _expect_count(name, args, 1, line, column)
                return args[0] in self.items
            case "vider":
                _expect_count(name, args, 0, line, column)
                self.items.clear()
                return None
            case "premier" | "dernier" | "element":
                raise sac_no_order_access(name, line, column)
            case _:
                raise unknown_object_method(self.type_name, name, line, column)


@dataclass
class Carnet(ObjetSac):
    entries: dict[str, Value] = field(default_factory=dict)
    order: list[str] = field(default_factory=list)

    @property
    def type_name(self) -> str:
        return "carnet"

    def describe(self) -> str:
        pairs = ", ".join(f"{key}: {format_value(value)}" for key, value in self.entries.items())
        return f"carnet [{pairs}]"

    def call_method(
        self,
        name: str,
        args: list[Value],
        line: int,
        column: int,
    ) -> Value | None:
        match name:
            case "etiqueter":
                _expect_count(name, args, 2, line, column)
                self._etiqueter(args[0], args[1], line, column)
                return None
            case "element":
                _expect_count(name, args, 1, line, column)
                return self._element(args[0], line, column)
            case "contient":
                _expect_count(name, args, 1, line, column)
                return self._key(args[0], line, column) in self.entries
            case "etiquettes":
                _expect_count(name, args, 0, line, column)
                return Rangee(items=[key for key in self.order])
            case "taille":
                _expect_count(name, args, 0, line, column)
                return len(self.entries)
            case "vider":
                _expect_count(name, args, 0, line, column)
                self.entries.clear()
                self.order.clear()
                return None
            case _:
                raise unknown_object_method(self.type_name, name, line, column)

    def _etiqueter(self, key: Value, value: Value, line: int, column: int) -> None:
        label = self._key(key, line, column)
        if label not in self.entries:
            self.order.append(label)
        self.entries[label] = value

    def _element(self, key: Value, line: int, column: int) -> Value:
        label = self._key(key, line, column)
        if label not in self.entries:
            raise carnet_key_missing(label, line, column)
        return self.entries[label]

    def _key(self, key: Value, line: int, column: int) -> str:
        if isinstance(key, str):
            return key
        if isinstance(key, (int, float)) and not isinstance(key, bool):
            return str(int(key) if float(key).is_integer() else key)
        raise carnet_key_missing(str(key), line, column)


@dataclass
class Tas(ObjetSac):
    items: list[Value] = field(default_factory=list)

    @property
    def type_name(self) -> str:
        return "tas"

    def describe(self) -> str:
        inner = ", ".join(format_value(item) for item in self.items)
        return f"tas [{inner}]"

    def call_method(
        self,
        name: str,
        args: list[Value],
        line: int,
        column: int,
    ) -> Value | None:
        match name:
            case "empiler":
                _expect_count(name, args, 1, line, column)
                self.items.append(args[0])
                return None
            case "depiler":
                _expect_count(name, args, 0, line, column)
                if not self.items:
                    raise empty_collection(self.type_name, "depiler", line, column)
                return self.items.pop()
            case "taille":
                _expect_count(name, args, 0, line, column)
                return len(self.items)
            case "vide":
                _expect_count(name, args, 0, line, column)
                return len(self.items) == 0
            case _:
                raise unknown_object_method(self.type_name, name, line, column)


@dataclass
class File(ObjetSac):
    items: list[Value] = field(default_factory=list)

    @property
    def type_name(self) -> str:
        return "file"

    def describe(self) -> str:
        inner = ", ".join(format_value(item) for item in self.items)
        return f"file [{inner}]"

    def call_method(
        self,
        name: str,
        args: list[Value],
        line: int,
        column: int,
    ) -> Value | None:
        match name:
            case "enfiler":
                _expect_count(name, args, 1, line, column)
                self.items.append(args[0])
                return None
            case "defiler":
                _expect_count(name, args, 0, line, column)
                if not self.items:
                    raise empty_collection(self.type_name, "defiler", line, column)
                return self.items.pop(0)
            case "taille":
                _expect_count(name, args, 0, line, column)
                return len(self.items)
            case "vide":
                _expect_count(name, args, 0, line, column)
                return len(self.items) == 0
            case _:
                raise unknown_object_method(self.type_name, name, line, column)


OBJECT_TYPES: dict[str, Callable[[], ObjetSac]] = {
    "rangée": Rangee,
    "sac": Sac,
    "carnet": Carnet,
    "tas": Tas,
    "file": File,
}


def is_object_type(name: str) -> bool:
    return name in OBJECT_TYPES


def create_object(type_name: str) -> ObjetSac:
    return OBJECT_TYPES[type_name]()
