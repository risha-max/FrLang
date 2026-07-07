from __future__ import annotations

from dataclasses import dataclass

from frlang.functions import Parameter, copy_value
from frlang.messages import no_matching_constructor
from frlang.lexer import Token
from frlang.objects import FrLangObject, Mots
from frlang.types import ClassType, TypeSpec, Value, VarType, format_value, is_nothing, is_object_var_type, is_pointer_type, is_primitive_var_type, NOTHING
from frlang.variables import Variable


@dataclass
class ClassField:
    name: str
    var_type: TypeSpec
    default_value: Value


@dataclass
class ClassConstructor:
    params: list[Parameter]
    body_tokens: list[Token]
    line: int
    column: int


@dataclass
class ClassMethod:
    name: str
    params: list[Parameter]
    return_type: TypeSpec | None
    body_tokens: list[Token]
    line: int
    column: int
    builtin_handler: str | None = None


@dataclass
class ClassDef:
    name: str
    parent_name: str
    fields: list[ClassField]
    methods: dict[str, ClassMethod]
    constructors: list[ClassConstructor]
    line: int
    column: int

    def field_map(self) -> dict[str, ClassField]:
        return {field_def.name: field_def for field_def in self.fields}

    def resolve_method(self, name: str, registry: dict[str, ClassDef]) -> ClassMethod | None:
        if name in self.methods:
            return self.methods[name]
        if not self.parent_name:
            return None
        parent = registry.get(self.parent_name)
        if parent is None:
            return None
        return parent.resolve_method(name, registry)

    def collect_fields(self, registry: dict[str, ClassDef]) -> list[ClassField]:
        if not self.parent_name:
            return list(self.fields)
        parent = registry.get(self.parent_name)
        if parent is None:
            return list(self.fields)
        merged = {field_def.name: field_def for field_def in parent.collect_fields(registry)}
        merged.update(self.field_map())
        return list(merged.values())


ORIGINAL_CLASS_NAME = "Original"


def create_original_class() -> ClassDef:
    return ClassDef(
        name=ORIGINAL_CLASS_NAME,
        parent_name="",
        fields=[],
        methods={
            "afficher": ClassMethod(
                name="afficher",
                params=[],
                return_type=None,
                body_tokens=[],
                line=1,
                column=1,
                builtin_handler="afficher",
            ),
            "equals": ClassMethod(
                name="equals",
                params=[Parameter("autre", ClassType(ORIGINAL_CLASS_NAME))],
                return_type=VarType.LOGIQUE,
                body_tokens=[],
                line=1,
                column=1,
                builtin_handler="equals",
            ),
        },
        constructors=[],
        line=1,
        column=1,
    )


class UserInstance(FrLangObject):
    __slots__ = ("class_name", "fields", "_interpreter")

    def __init__(
        self,
        interpreter: object,
        class_name: str,
        fields: dict[str, Variable],
    ) -> None:
        self._interpreter = interpreter
        self.class_name = class_name
        self.fields = fields

    @property
    def type_name(self) -> str:
        return self.class_name

    def describe(self) -> str:
        if not self.fields:
            return f"{self.class_name} {{}}"
        parts = [f"{name}={format_value(var.value)}" for name, var in self.fields.items()]
        return f"{self.class_name} {{ {', '.join(parts)} }}"

    def call_method(
        self,
        name: str,
        args: list[Value],
        line: int,
        column: int,
    ) -> Value | None:
        interpreter = self._interpreter
        return interpreter._call_instance_method(self, name, args, line, column)  # type: ignore[attr-defined]


def instantiate_class(
    interpreter: object,
    class_def: ClassDef,
    registry: dict[str, ClassDef],
    args: list[Value] | None = None,
    *,
    line: int,
    column: int,
) -> UserInstance:
    arg_values = list(args or [])
    fields: dict[str, Variable] = {}
    for field_def in class_def.collect_fields(registry):
        if field_def.name in fields:
            continue
        default = field_def.default_value
        value = copy_value(default) if is_object_var_type(field_def.var_type) or not isinstance(
            default, (int, float, str, bool)
        ) else default
        fields[field_def.name] = Variable(field_def.var_type, value)

    instance = UserInstance(interpreter, class_def.name, fields)
    constructor = _resolve_constructor(class_def, len(arg_values))
    if constructor is None:
        if arg_values:
            raise no_matching_constructor(class_def.name, len(arg_values), line, column)
        return instance

    interpreter._execute_constructor(instance, constructor, arg_values, line, column)  # type: ignore[attr-defined]
    return instance


def _resolve_constructor(class_def: ClassDef, argc: int) -> ClassConstructor | None:
    if not class_def.constructors:
        return None
    matches = [ctor for ctor in class_def.constructors if len(ctor.params) == argc]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        return None
    return matches[0]


def instances_equal(left: UserInstance, right: UserInstance) -> bool:
    if left.class_name != right.class_name:
        return False
    for name, left_var in left.fields.items():
        right_var = right.fields.get(name)
        if right_var is None:
            return False
        if not _field_values_equal(left_var.value, right_var.value):
            return False
    return True


def _field_values_equal(left: Value, right: Value) -> bool:
    return values_equal(left, right)


def values_equal(left: Value, right: Value) -> bool:
    if is_nothing(left) or is_nothing(right):
        return is_nothing(left) and is_nothing(right)
    if isinstance(left, Mots) and isinstance(right, Mots):
        return left.text == right.text
    if isinstance(left, FrLangObject) or isinstance(right, FrLangObject):
        return left is right
    return left == right
