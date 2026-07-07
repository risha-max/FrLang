from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Pointer:
    """Pointeur vers une variable Sac (partage la même boîte)."""

    target: Any
    target_name: str

    @property
    def address_hex(self) -> str:
        return self.target.address_hex

    def copy(self) -> Pointer:
        return Pointer(target=self.target, target_name=self.target_name)
