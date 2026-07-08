from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from frlang.memory import is_primitive_array


@dataclass
class Pointer:
    """Pointeur vers une variable FrLang (partage la même boîte)."""

    target: Any
    target_name: str
    offset: int = 0

    def _addressable_storage(self) -> Any | None:
        value = self.target.value
        if is_primitive_array(value):
            return value
        memory = getattr(self.target, "_memory", None)
        if memory is not None:
            return memory
        return None

    @property
    def address_hex(self) -> str:
        storage = self._addressable_storage()
        if storage is not None and hasattr(storage, "element_address_hex"):
            return storage.element_address_hex(self.offset)
        if storage is not None and self.offset == 0 and hasattr(storage, "address_hex"):
            return storage.address_hex
        return self.target.address_hex

    @property
    def display_name(self) -> str:
        if self.offset == 0:
            return self.target_name
        return f"{self.target_name}[{self.offset}]"

    def copy(self) -> Pointer:
        return Pointer(target=self.target, target_name=self.target_name, offset=self.offset)

    def with_offset(self, delta: int) -> Pointer:
        return Pointer(
            target=self.target,
            target_name=self.target_name,
            offset=self.offset + delta,
        )
