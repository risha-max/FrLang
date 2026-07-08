from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias

from frlang.pointers import Pointer


class NothingType:
    __slots__ = ()

    def __repr__(self) -> str:
        return "rien"


NOTHING = NothingType()


def is_nothing(value: object) -> bool:
    return value is NOTHING


class VarType(Enum):
    NOMBRE = "nombre"
    MOTS = "Mots"
    LOGIQUE = "logique"
    RANGEE = "Rangee"
    SAC = "Sac"
    CARNET = "Carnet"
    TAS = "Tas"
    FILE = "File"


@dataclass(frozen=True, slots=True)
class PointerType:
    target: VarType | ClassType

    @property
    def value(self) -> str:
        if isinstance(self.target, ClassType):
            return f"pointeur {self.target.name}"
        return f"pointeur {self.target.value}"


@dataclass(frozen=True, slots=True)
class ClassType:
    name: str

    @property
    def value(self) -> str:
        return self.name


@dataclass(frozen=True, slots=True)
class ArrayType:
    element: VarType
    size: int

    @property
    def value(self) -> str:
        return f"{self.element.value}[{self.size}]"


TypeSpec: TypeAlias = VarType | PointerType | ClassType | ArrayType
StoredValue: TypeAlias = int | float | str | bool | list | object | Pointer | NothingType
Value: TypeAlias = int | float | str | bool | list | object | NothingType


def parse_type_name(name: str) -> VarType | None:
    for var_type in VarType:
        if var_type.value == name:
            return var_type
    return None


def is_capitalized_type_name(name: str) -> bool:
    return bool(name) and name[0].isupper()


_LEGACY_OBJECT_TYPE_NAMES: dict[str, VarType] = {
    "rangée": VarType.RANGEE,
    "sac": VarType.SAC,
    "carnet": VarType.CARNET,
    "tas": VarType.TAS,
    "file": VarType.FILE,
    "mots": VarType.MOTS,
}


def legacy_object_type_name(name: str) -> VarType | None:
    return _LEGACY_OBJECT_TYPE_NAMES.get(name)


def format_type_name(type_spec: TypeSpec) -> str:
    if isinstance(type_spec, (PointerType, ClassType, ArrayType)):
        return type_spec.value
    return type_spec.value


def is_array_type(type_spec: TypeSpec) -> bool:
    return isinstance(type_spec, ArrayType)


def array_element_type(type_spec: TypeSpec) -> VarType | None:
    if isinstance(type_spec, ArrayType):
        return type_spec.element
    return None


def array_size(type_spec: TypeSpec) -> int | None:
    if isinstance(type_spec, ArrayType):
        return type_spec.size
    return None


def is_class_type(type_spec: TypeSpec) -> bool:
    return isinstance(type_spec, ClassType)


def is_pointer_type(type_spec: TypeSpec) -> bool:
    return isinstance(type_spec, PointerType)


def pointer_target_type(type_spec: TypeSpec) -> VarType | ClassType | None:
    if isinstance(type_spec, PointerType):
        return type_spec.target
    return None


def is_primitive_var_type(var_type: VarType) -> bool:
    return var_type in {VarType.NOMBRE, VarType.LOGIQUE}


def is_object_var_type(var_type: VarType) -> bool:
    return var_type in {
        VarType.MOTS,
        VarType.RANGEE,
        VarType.SAC,
        VarType.CARNET,
        VarType.TAS,
        VarType.FILE,
    }


def is_collection_var_type(var_type: VarType) -> bool:
    return var_type in {
        VarType.RANGEE,
        VarType.SAC,
        VarType.CARNET,
        VarType.TAS,
        VarType.FILE,
    }


def format_pointer(pointer: Pointer) -> str:
    return (
        f"L'adresse hexadécimale de {pointer.target_name} est {pointer.address_hex}"
    )


def format_value(value: StoredValue) -> str:
    if is_nothing(value):
        return "rien"
    if isinstance(value, Pointer):
        return format_pointer(value)
    if isinstance(value, list):
        inner = ", ".join(format_value(item) for item in value)
        return f"[{inner}]"
    if hasattr(value, "describe") and callable(value.describe):
        return str(value.describe())
    if isinstance(value, bool):
        return "vrai" if value else "faux"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)
