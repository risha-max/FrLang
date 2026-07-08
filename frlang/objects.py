from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from frlang.messages import (
    carnet_key_missing,
    empty_collection,
    fichier_introuvable,
    fichier_ligne_hors_limites,
    index_out_of_range,
    mots_not_a_number,
    sac_no_order_access,
    unknown_object_method,
    wrong_constructor_argument_count,
    wrong_method_argument_count,
)
from frlang.types import (
    NOTHING,
    ClassType,
    TypeSpec,
    Value,
    VarType,
    format_value,
    is_array_type,
    is_object_var_type,
    is_pointer_type,
    is_primitive_var_type,
)


class FrLangObject(ABC):
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
class Rangee(FrLangObject):
    items: list[Value] = field(default_factory=list)

    @property
    def type_name(self) -> str:
        return "Rangee"

    def describe(self) -> str:
        inner = ", ".join(format_value(item) for item in self.items)
        return f"Rangee [{inner}]"

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
class Sac(FrLangObject):
    items: list[Value] = field(default_factory=list)

    @property
    def type_name(self) -> str:
        return "Sac"

    def describe(self) -> str:
        inner = ", ".join(format_value(item) for item in self.items)
        return f"Sac [{inner}]"

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
class Carnet(FrLangObject):
    entries: dict[str, Value] = field(default_factory=dict)
    order: list[str] = field(default_factory=list)

    @property
    def type_name(self) -> str:
        return "Carnet"

    def describe(self) -> str:
        pairs = ", ".join(f"{key}: {format_value(value)}" for key, value in self.entries.items())
        return f"Carnet [{pairs}]"

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
class Tas(FrLangObject):
    items: list[Value] = field(default_factory=list)

    @property
    def type_name(self) -> str:
        return "Tas"

    def describe(self) -> str:
        inner = ", ".join(format_value(item) for item in self.items)
        return f"Tas [{inner}]"

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
class File(FrLangObject):
    items: list[Value] = field(default_factory=list)

    @property
    def type_name(self) -> str:
        return "File"

    def describe(self) -> str:
        inner = ", ".join(format_value(item) for item in self.items)
        return f"File [{inner}]"

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


@dataclass
class Mots(FrLangObject):
    text: str = ""

    @property
    def type_name(self) -> str:
        return "Mots"

    def describe(self) -> str:
        return self.text

    def call_method(
        self,
        name: str,
        args: list[Value],
        line: int,
        column: int,
    ) -> Value | None:
        match name:
            case "inverser":
                _expect_count(name, args, 0, line, column)
                return Mots(self.text[::-1])
            case "equals":
                _expect_count(name, args, 1, line, column)
                other = args[0]
                if isinstance(other, Mots):
                    return self.text == other.text
                return False
            case "taille":
                _expect_count(name, args, 0, line, column)
                return len(self.text)
            case "caractere":
                _expect_count(name, args, 1, line, column)
                return self._caractere(args[0], line, column)
            case "concatener":
                _expect_count(name, args, 1, line, column)
                other = args[0]
                if not isinstance(other, Mots):
                    raise unknown_object_method(self.type_name, name, line, column)
                return Mots(self.text + other.text)
            case "en_nombre":
                _expect_count(name, args, 0, line, column)
                return self._en_nombre(line, column)
            case _:
                raise unknown_object_method(self.type_name, name, line, column)

    def _en_nombre(self, line: int, column: int) -> int | float:
        text = self.text.strip()
        if not text:
            raise mots_not_a_number(self.text, line, column)
        try:
            if "." in text:
                value = float(text)
                return int(value) if value.is_integer() else value
            return int(text)
        except ValueError:
            raise mots_not_a_number(self.text, line, column)

    def _caractere(self, position: Value, line: int, column: int) -> Mots:
        if isinstance(position, bool) or not isinstance(position, (int, float)):
            raise index_out_of_range(self.type_name, position, len(self.text), line, column)
        index = int(position)
        if index < 1 or index > len(self.text):
            raise index_out_of_range(self.type_name, index, len(self.text), line, column)
        return Mots(self.text[index - 1])


@dataclass
class Fichier(FrLangObject):
    path: str = ""
    base_dir: Path = field(default_factory=Path.cwd)
    _written: bool = False

    @property
    def type_name(self) -> str:
        return "Fichier"

    def describe(self) -> str:
        return f"Fichier({self.path})"

    def resolved_path(self) -> Path:
        candidate = Path(self.path)
        if candidate.is_absolute():
            return candidate
        return (self.base_dir / candidate).resolve()

    def _read_lines(self, line: int, column: int) -> list[str]:
        path = self.resolved_path()
        if not path.exists():
            raise fichier_introuvable(self.path, line, column)
        return path.read_text(encoding="utf-8").splitlines()

    def call_method(
        self,
        name: str,
        args: list[Value],
        line: int,
        column: int,
    ) -> Value | None:
        match name:
            case "ecrire":
                _expect_count(name, args, 1, line, column)
                path = self.resolved_path()
                path.parent.mkdir(parents=True, exist_ok=True)
                mode = "a" if self._written else "w"
                with path.open(mode, encoding="utf-8") as handle:
                    handle.write(format_value(args[0]))
                    handle.write("\n")
                self._written = True
                return None
            case "lire":
                _expect_count(name, args, 0, line, column)
                path = self.resolved_path()
                if not path.exists():
                    raise fichier_introuvable(self.path, line, column)
                return Mots(path.read_text(encoding="utf-8"))
            case "lire_ligne":
                _expect_count(name, args, 1, line, column)
                lines = self._read_lines(line, column)
                position = args[0]
                if isinstance(position, bool) or not isinstance(position, (int, float)):
                    raise fichier_ligne_hors_limites(position, len(lines), line, column)
                index = int(position)
                if index < 1 or index > len(lines):
                    raise fichier_ligne_hors_limites(index, len(lines), line, column)
                return Mots(lines[index - 1])
            case "fermer":
                _expect_count(name, args, 0, line, column)
                return None
            case "existe":
                _expect_count(name, args, 0, line, column)
                return self.resolved_path().exists()
            case "chemin":
                _expect_count(name, args, 0, line, column)
                return Mots(str(self.resolved_path()))
            case "taille":
                _expect_count(name, args, 0, line, column)
                path = self.resolved_path()
                if not path.exists():
                    return 0
                return path.stat().st_size
            case _:
                raise unknown_object_method(self.type_name, name, line, column)


OBJECT_TYPES: dict[str, Callable[[], FrLangObject]] = {
    "Mots": Mots,
    "Rangee": Rangee,
    "Sac": Sac,
    "Carnet": Carnet,
    "Tas": Tas,
    "File": File,
    "Fichier": Fichier,
}


def is_object_type(name: str) -> bool:
    return name in OBJECT_TYPES


def create_object(type_name: str) -> FrLangObject:
    return OBJECT_TYPES[type_name]()


def fill_list_object(obj: FrLangObject, args: list[Value], line: int, column: int) -> FrLangObject:
    if isinstance(obj, Rangee):
        obj.items = list(args)
        return obj
    if isinstance(obj, Sac):
        items: list[Value] = []
        for value in args:
            if value not in items:
                items.append(value)
        obj.items = items
        return obj
    if isinstance(obj, (Tas, File)):
        obj.items = list(args)
        return obj
    raise wrong_constructor_argument_count(obj.type_name, 0, len(args), line, column)


def fill_carnet_object(
    carnet: Carnet,
    entries: dict[str, Value],
    line: int,
    column: int,
) -> Carnet:
    for label, value in entries.items():
        carnet._etiqueter(label, value, line, column)
    return carnet


def fill_mots_object(
    obj: FrLangObject,
    args: list[Value],
    line: int,
    column: int,
) -> Mots:
    if not isinstance(obj, Mots):
        raise wrong_constructor_argument_count(obj.type_name, 0, len(args), line, column)
    if len(args) > 1:
        raise wrong_constructor_argument_count(obj.type_name, 1, len(args), line, column)
    if not args:
        return obj
    arg = args[0]
    if isinstance(arg, str):
        return Mots(arg)
    if isinstance(arg, Mots):
        return Mots(arg.text)
    raise wrong_constructor_argument_count(obj.type_name, 1, len(args), line, column)


def fill_fichier_object(
    obj: FrLangObject,
    args: list[Value],
    line: int,
    column: int,
) -> Fichier:
    if not isinstance(obj, Fichier):
        raise wrong_constructor_argument_count(obj.type_name, 1, len(args), line, column)
    if len(args) != 1:
        raise wrong_constructor_argument_count(obj.type_name, 1, len(args), line, column)
    arg = args[0]
    if isinstance(arg, Mots):
        obj.path = arg.text
        return obj
    if isinstance(arg, str):
        obj.path = arg
        return obj
    raise wrong_constructor_argument_count(obj.type_name, 1, len(args), line, column)


def default_value_for_type(type_spec: TypeSpec) -> Value:
    if is_pointer_type(type_spec):
        return NOTHING
    if isinstance(type_spec, ClassType):
        raise ValueError(f"Pas de valeur par défaut pour la classe {type_spec.name}")
    if is_array_type(type_spec):
        size = type_spec.size
        return [NOTHING] * size
    assert isinstance(type_spec, VarType)
    if is_primitive_var_type(type_spec):
        return NOTHING
    if is_object_var_type(type_spec):
        return create_object(type_spec.value)
    raise ValueError(f"Type inconnu : {type_spec}")


COLLECTION_TYPE_NAMES: frozenset[str] = frozenset(
    {VarType.RANGEE.value, VarType.SAC.value, VarType.CARNET.value, VarType.TAS.value, VarType.FILE.value}
)


def is_collection_object(value: object) -> bool:
    return isinstance(value, (Rangee, Sac, Carnet, Tas, File))


def iterate_collection(obj: FrLangObject) -> list[Value]:
    if isinstance(obj, Rangee):
        return list(obj.items)
    if isinstance(obj, Sac):
        return list(obj.items)
    if isinstance(obj, Tas):
        return list(obj.items)
    if isinstance(obj, File):
        return list(obj.items)
    if isinstance(obj, Carnet):
        return [obj.entries[key] for key in obj.order]
    raise TypeError(f"Objet non itérable : {obj.type_name}")


def _as_range_int(value: Value, name: str, line: int, column: int) -> int:
    from frlang.messages import range_requires_integer

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise range_requires_integer(name, line, column)
    if isinstance(value, float) and not value.is_integer():
        raise range_requires_integer(name, line, column)
    return int(value)


def build_range(args: list[Value], line: int, column: int) -> Rangee:
    from frlang.messages import range_step_cannot_be_zero, range_wrong_argument_count

    if not args or len(args) > 3:
        raise range_wrong_argument_count(len(args), line, column)

    if len(args) == 1:
        start, stop, step = 0, _as_range_int(args[0], "stop", line, column), 1
    elif len(args) == 2:
        start = _as_range_int(args[0], "start", line, column)
        stop = _as_range_int(args[1], "stop", line, column)
        step = 1
    else:
        start = _as_range_int(args[0], "start", line, column)
        stop = _as_range_int(args[1], "stop", line, column)
        step = _as_range_int(args[2], "step", line, column)

    if step == 0:
        raise range_step_cannot_be_zero(line, column)

    items: list[Value] = []
    current = start
    if step > 0:
        while current < stop:
            items.append(current)
            current += step
    else:
        while current > stop:
            items.append(current)
            current += step
    return Rangee(items=items)
