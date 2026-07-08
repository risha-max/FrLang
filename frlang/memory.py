from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from frlang.types import Value

_INT64 = ctypes.c_int64
_BOOL = ctypes.c_bool
_DOUBLE = ctypes.c_double


def _is_rien(value: object) -> bool:
    from frlang.types import is_nothing

    return is_nothing(value)


def _rien() -> object:
    from frlang.types import NOTHING

    return NOTHING


def _hex_address(cell: ctypes._CData) -> str:
    return f"0x{ctypes.addressof(cell):012x}"


class NumberCell:
    __slots__ = ("_cell", "_is_float", "_rien")

    def __init__(self, value: object | None = None) -> None:
        if value is None:
            value = _rien()
        self._rien = _is_rien(value)
        self._is_float = False
        if self._rien:
            self._cell = _INT64(0)
            return
        if isinstance(value, float):
            self._is_float = True
            self._cell = _DOUBLE(value)
        else:
            self._cell = _INT64(int(value))

    @property
    def address_hex(self) -> str:
        return _hex_address(self._cell)

    def python_value(self) -> Value:
        if self._rien:
            return _rien()  # type: ignore[return-value]
        raw = self._cell.value
        if self._is_float:
            return float(raw)
        return int(raw)

    def set(self, value: object) -> None:
        if _is_rien(value):
            self._rien = True
            return
        self._rien = False
        if isinstance(value, float):
            if not self._is_float:
                self._cell = _DOUBLE(value)
                self._is_float = True
            else:
                self._cell.value = value
        else:
            if self._is_float:
                self._cell = _INT64(int(value))
                self._is_float = False
            else:
                self._cell.value = int(value)


class LogicCell:
    __slots__ = ("_cell", "_rien")

    def __init__(self, value: object | None = None) -> None:
        if value is None:
            value = _rien()
        self._rien = _is_rien(value)
        self._cell = _BOOL(False if self._rien else bool(value))

    @property
    def address_hex(self) -> str:
        return _hex_address(self._cell)

    def python_value(self) -> Value:
        if self._rien:
            return _rien()  # type: ignore[return-value]
        return bool(self._cell.value)

    def set(self, value: object) -> None:
        if _is_rien(value):
            self._rien = True
            return
        self._rien = False
        self._cell.value = bool(value)


class NumberArray:
    ELEMENT_SIZE = ctypes.sizeof(_INT64)
    __slots__ = ("_cells", "_rien", "_size")

    def __init__(self, size: int, items: list[Value] | None = None) -> None:
        self._size = size
        self._cells = (_INT64 * size)()
        self._rien = [True] * size
        if items is not None:
            for index, item in enumerate(items):
                self._set(index, item)

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int) -> Value:
        if self._rien[index]:
            return _rien()  # type: ignore[return-value]
        return int(self._cells[index])

    def __setitem__(self, index: int, value: Value) -> None:
        self._set(index, value)

    def __iter__(self) -> Iterator[Value]:
        for index in range(self._size):
            yield self[index]

    @property
    def address_hex(self) -> str:
        return _hex_address(self._cells)

    def element_address_hex(self, index: int) -> str:
        base = ctypes.addressof(self._cells)
        return f"0x{base + index * self.ELEMENT_SIZE:012x}"

    def copy(self) -> NumberArray:
        duplicate = NumberArray(self._size)
        duplicate._cells = (_INT64 * self._size)(*self._cells)
        duplicate._rien = list(self._rien)
        return duplicate

    def _set(self, index: int, value: object) -> None:
        if _is_rien(value):
            self._rien[index] = True
            return
        self._rien[index] = False
        self._cells[index] = int(value)


class LogicArray:
    ELEMENT_SIZE = ctypes.sizeof(_BOOL)
    __slots__ = ("_cells", "_rien", "_size")

    def __init__(self, size: int, items: list[Value] | None = None) -> None:
        self._size = size
        self._cells = (_BOOL * size)()
        self._rien = [True] * size
        if items is not None:
            for index, item in enumerate(items):
                self._set(index, item)

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int) -> Value:
        if self._rien[index]:
            return _rien()  # type: ignore[return-value]
        return bool(self._cells[index])

    def __setitem__(self, index: int, value: Value) -> None:
        self._set(index, value)

    def __iter__(self) -> Iterator[Value]:
        for index in range(self._size):
            yield self[index]

    @property
    def address_hex(self) -> str:
        return _hex_address(self._cells)

    def element_address_hex(self, index: int) -> str:
        base = ctypes.addressof(self._cells)
        return f"0x{base + index * self.ELEMENT_SIZE:012x}"

    def copy(self) -> LogicArray:
        duplicate = LogicArray(self._size)
        duplicate._cells = (_BOOL * self._size)(*self._cells)
        duplicate._rien = list(self._rien)
        return duplicate

    def _set(self, index: int, value: object) -> None:
        if _is_rien(value):
            self._rien[index] = True
            return
        self._rien[index] = False
        self._cells[index] = bool(value)


PrimitiveArray = NumberArray | LogicArray


def is_primitive_array(value: object) -> bool:
    return isinstance(value, (NumberArray, LogicArray))


def array_element_size(value: PrimitiveArray) -> int:
    if isinstance(value, NumberArray):
        return NumberArray.ELEMENT_SIZE
    return LogicArray.ELEMENT_SIZE


def make_primitive_array(element: object, size: int, items: list[Value] | None = None) -> PrimitiveArray:
    from frlang.types import VarType

    if element == VarType.NOMBRE:
        return NumberArray(size, items)
    if element == VarType.LOGIQUE:
        return LogicArray(size, items)
    raise ValueError(f"Type de tableau primitif inconnu : {element}")


def attach_scalar_memory(variable: object, var_type: object, value: object) -> None:
    from frlang.types import VarType, is_primitive_var_type

    if not isinstance(var_type, VarType) or not is_primitive_var_type(var_type):
        return
    if var_type == VarType.NOMBRE:
        variable._memory = NumberCell(value)  # type: ignore[attr-defined]
    elif var_type == VarType.LOGIQUE:
        variable._memory = LogicCell(value)  # type: ignore[attr-defined]


def sync_scalar_memory(variable: object, value: object) -> object:
    memory = getattr(variable, "_memory", None)
    if isinstance(memory, (NumberCell, LogicCell)):
        memory.set(value)
        return memory.python_value()
    return value
