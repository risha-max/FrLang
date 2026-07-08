from frlang.memory import is_primitive_array
from frlang.pointers import Pointer
from frlang.types import TypeSpec, Value


class Variable:
    __slots__ = ("var_type", "value", "_memory")

    def __init__(self, var_type: TypeSpec, value: Value | Pointer) -> None:
        self.var_type = var_type
        self.value = value
        self._memory = value if is_primitive_array(value) else None

    @property
    def address_hex(self) -> str:
        if is_primitive_array(self.value):
            return self.value.address_hex
        if self._memory is not None and hasattr(self._memory, "address_hex"):
            return self._memory.address_hex
        return f"0x{id(self):012x}"

