from sac.pointers import Pointer
from sac.types import TypeSpec, Value


class Variable:
    __slots__ = ("var_type", "value")

    def __init__(self, var_type: TypeSpec, value: Value | Pointer) -> None:
        self.var_type = var_type
        self.value = value

    @property
    def address_hex(self) -> str:
        return f"0x{id(self):012x}"

