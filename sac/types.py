from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias

from sac.pointers import Pointer


class VarType(Enum):
    NOMBRE = "nombre"
    MOTS = "mots"
    LOGIQUE = "logique"
    RANGEE = "rangée"
    SAC = "sac"
    CARNET = "carnet"
    TAS = "tas"
    FILE = "file"


@dataclass(frozen=True, slots=True)
class PointerType:
    target: VarType

    @property
    def value(self) -> str:
        return f"pointeur {self.target.value}"


TypeSpec: TypeAlias = VarType | PointerType
StoredValue: TypeAlias = int | float | str | bool | object | Pointer
Value: TypeAlias = int | float | str | bool | object


def parse_type_name(name: str) -> VarType | None:
    for var_type in VarType:
        if var_type.value == name:
            return var_type
    return None


def format_type_name(type_spec: TypeSpec) -> str:
    if isinstance(type_spec, PointerType):
        return type_spec.value
    return type_spec.value


def is_pointer_type(type_spec: TypeSpec) -> bool:
    return isinstance(type_spec, PointerType)


def pointer_target_type(type_spec: TypeSpec) -> VarType | None:
    if isinstance(type_spec, PointerType):
        return type_spec.target
    return None


def is_object_var_type(var_type: VarType) -> bool:
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
    if isinstance(value, Pointer):
        return format_pointer(value)
    if hasattr(value, "describe") and callable(value.describe):
        return str(value.describe())
    if isinstance(value, bool):
        return "vrai" if value else "faux"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)
