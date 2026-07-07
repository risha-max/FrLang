from frlang.classes import (
    ORIGINAL_CLASS_NAME,
    ClassConstructor,
    ClassDef,
    ClassField,
    ClassMethod,
    UserInstance,
    create_original_class,
    instantiate_class,
    instances_equal,
    values_equal,
)
from frlang.errors import ReturnSignal
from frlang.functions import Parameter, UserFunction, copy_value
from frlang.lexer import Lexer, Token, TokenKind
from frlang.messages import (
    adresse_requires_variable,
    assign_to_undefined,
    deprecated_object_literal_syntax,
    division_by_zero,
    empty_expression,
    empty_program,
    empty_statement,
    expected_equal,
    cannot_redefine_original,
    class_already_defined,
    duplicate_class_constructor,
    duplicate_class_field,
    duplicate_class_method,
    expected_class_name,
    expected_fonction_or_classe,
    expected_herite_de,
    expected_function_name,
    inheritance_cycle,
    expected_logique_condition,
    expected_method_parentheses,
    expected_parameter_list,
    expected_type,
    expected_type_after_nouveau,
    expected_type_after_pointeur,
    expected_value,
    expected_variable_name,
    function_already_defined,
    incomplete_expression,
    missing_closing_brace,
    missing_closing_paren,
    missing_return_statement,
    missing_semicolon,
    missing_value_after_equal,
    modulo_by_zero,
    nested_pointer_not_allowed,
    nothing_value_not_allowed,
    not_a_pointer,
    object_name_needs_capital,
    object_in_numeric_expression,
    pointer_operation_not_allowed,
    pointer_requires_valeur,
    pointer_type_mismatch,
    return_in_void_function,
    return_outside_function,
    rien_not_allowed_for_type,
    type_as_variable_name,
    type_in_expression,
    type_mismatch,
    type_requires_argument,
    type_wrong_argument_count,
    unexpected_symbol,
    expected_method_name,
    undefined_class,
    undefined_parent_class,
    unexpected_in_class,
    undefined_function,
    undefined_variable,
    unknown_instance_field,
    unknown_instance_method,
    use_nouveau_to_create,
    use_soit_for_declaration,
    variable_already_defined,
    wrong_constructor_argument_count,
    wrong_function_argument_count,
    wrong_type_in_expression,
)
from frlang.objects import (
    Carnet,
    FrLangObject,
    Mots,
    Rangee,
    Sac,
    create_object,
    default_value_for_type,
    fill_carnet_object,
    fill_list_object,
    fill_mots_object,
    is_object_type,
)
from frlang.pointers import Pointer
from frlang.types import (
    ClassType,
    PointerType,
    TypeSpec,
    Value,
    VarType,
    format_type_name,
    format_value,
    is_capitalized_type_name,
    is_class_type,
    is_nothing,
    is_object_var_type,
    is_pointer_type,
    is_primitive_var_type,
    legacy_object_type_name,
    NOTHING,
    parse_type_name,
    pointer_target_type,
)
from frlang.variables import Variable


class Interpreter:
    """Interprète des expressions et de petits programmes avec variables."""

    def __init__(self, source: str) -> None:
        self._tokens = Lexer(source).tokenize()
        self._position = 0
        self._scopes: list[dict[str, Variable]] = [{}]
        self._functions: dict[str, UserFunction] = {}
        self._classes: dict[str, ClassDef] = {ORIGINAL_CLASS_NAME: create_original_class()}
        self._current_class_name: str | None = None
        self.output: list[str] = []

    @classmethod
    def session(cls) -> Interpreter:
        interpreter = object.__new__(cls)
        interpreter._tokens = []
        interpreter._position = 0
        interpreter._scopes = [{}]
        interpreter._functions = {}
        interpreter._classes = {ORIGINAL_CLASS_NAME: create_original_class()}
        interpreter._current_class_name = None
        interpreter.output = []
        return interpreter

    def run(self) -> Value | None:
        if self._is_at_end():
            raise empty_program()

        return self._run_source()

    def execute(self, source: str) -> Value | None:
        stripped = source.strip()
        if not stripped:
            return None

        self._tokens = Lexer(source).tokenize()
        self._position = 0
        if self._is_at_end():
            return None

        return self._run_source()

    def _run_source(self) -> Value | None:
        if self._is_program():
            return self._run_program()

        value = self._numeric_expression()
        if not self._is_at_end():
            token = self._peek()
            raise unexpected_symbol(str(token.value), token.line, token.column)
        return value

    def parse(self) -> Value:
        result = self.run()
        if result is None:
            raise empty_expression()
        return result

    def _is_program(self) -> bool:
        program_kinds = {
            TokenKind.SOIT,
            TokenKind.AFFICHER,
            TokenKind.DEFINIR,
            TokenKind.SI,
            TokenKind.TANT,
            TokenKind.SEMICOLON,
            TokenKind.EQUAL,
            TokenKind.DOT,
            TokenKind.LBRACKET,
            TokenKind.LBRACE,
        }
        return any(
            token.kind in program_kinds for token in self._tokens if token.kind != TokenKind.EOF
        )

    def _run_program(self) -> Value | None:
        result: Value | None = None

        while not self._is_at_end():
            if self._check(TokenKind.SEMICOLON):
                token = self._advance()
                raise empty_statement(token.line, token.column)

            if self._check(TokenKind.SOIT):
                self._advance()
                self._declaration()
            elif self._check(TokenKind.DEFINIR):
                self._advance()
                self._define_dispatch()
            elif self._check(TokenKind.AFFICHER):
                self._advance()
                self._afficher()
            elif self._check(TokenKind.IDENTIFIER) and str(self._peek().value) == "valeur":
                if self._peek_next().kind == TokenKind.LPAREN and self._is_valeur_assignment():
                    self._pointer_assignment()
                else:
                    result = self._statement_expression()
                    self._consume_semicolon()
            elif self._check(TokenKind.IDENTIFIER) and self._peek_next().kind == TokenKind.EQUAL:
                name = self._advance()
                raise use_soit_for_declaration(
                    str(name.value),
                    name.line,
                    name.column,
                )
            elif self._check(TokenKind.IDENTIFIER) and self._peek_next().kind == TokenKind.DOT:
                result = self._value_expression()
                self._consume_semicolon()
            elif self._check(TokenKind.SI):
                self._advance()
                try:
                    self._if_statement()
                except ReturnSignal as signal:
                    raise return_outside_function(self._previous().line, self._previous().column) from signal
            elif self._check(TokenKind.TANT):
                self._advance()
                try:
                    self._while_statement()
                except ReturnSignal as signal:
                    raise return_outside_function(self._previous().line, self._previous().column) from signal
            elif self._check(TokenKind.RETOURNE):
                token = self._peek()
                raise return_outside_function(token.line, token.column)
            else:
                result = self._statement_expression()
                self._consume_semicolon()

        return result

    def _afficher(self) -> None:
        if self._check(TokenKind.SOIT):
            self._advance()
            value = self._declaration(consume_semicolon=False)
        else:
            value = self._display_expression()

        self._consume_semicolon()
        self.output.append(format_value(value))

    def _declaration(self, *, consume_semicolon: bool = True) -> Value:
        var_type = self._parse_type()
        name_token = self._consume_variable_name()
        name = str(name_token.value)

        if name in self._current_scope():
            existing = self._current_scope()[name]
            raise variable_already_defined(
                name,
                format_type_name(existing.var_type),
                format_type_name(var_type),
                name_token.line,
                name_token.column,
            )

        if self._match(TokenKind.EQUAL):
            if self._check(TokenKind.SEMICOLON):
                token = self._peek()
                raise missing_value_after_equal(name, token.line, token.column)
            value = self._value_for_type(var_type, name, name_token.line, name_token.column)
        else:
            value = default_value_for_type(var_type)
        if consume_semicolon:
            self._consume_semicolon()

        self._check_value_type(name, var_type, value, name_token.line, name_token.column)
        self._current_scope()[name] = Variable(var_type, value)
        return value

    def _define_dispatch(self) -> None:
        if self._match(TokenKind.FONCTION):
            self._define_function()
            return
        if self._match(TokenKind.CLASSE):
            self._define_class()
            return
        token = self._peek()
        raise expected_fonction_or_classe(token.line, token.column)

    def _define_function(self) -> None:
        name_token = self._consume_function_name()
        name = str(name_token.value)

        if name in self._functions:
            raise function_already_defined(name, name_token.line, name_token.column)

        self._consume(TokenKind.LPAREN, expected_parameter_list)
        params = self._parse_function_parameters()
        if not self._match(TokenKind.RPAREN):
            token = self._peek()
            raise missing_closing_paren(token.line, token.column)

        if not self._match(TokenKind.LBRACE):
            token = self._peek()
            raise expected_value("{", token.line, token.column)

        body_tokens = self._skip_block_body()

        return_type: TypeSpec | None = None
        if self._match(TokenKind.RETOURNE):
            return_type = self._parse_type()

        self._functions[name] = UserFunction(
            name=name,
            params=params,
            return_type=return_type,
            body_tokens=body_tokens,
            line=name_token.line,
            column=name_token.column,
        )

    def _define_class(self) -> None:
        name_token = self._consume(TokenKind.IDENTIFIER, expected_class_name)
        name = str(name_token.value)
        self._ensure_capitalized_type_name(name, name_token.line, name_token.column)

        if name == ORIGINAL_CLASS_NAME:
            raise cannot_redefine_original(name_token.line, name_token.column)
        if name in self._classes:
            raise class_already_defined(name, name_token.line, name_token.column)

        parent_name = ORIGINAL_CLASS_NAME
        if self._match(TokenKind.HERITE):
            if not self._match(TokenKind.DE):
                token = self._peek()
                raise expected_herite_de(token.line, token.column)
            parent_token = self._consume(TokenKind.IDENTIFIER, expected_class_name)
            parent_name = str(parent_token.value)
            if parent_name not in self._classes:
                raise undefined_parent_class(parent_name, parent_token.line, parent_token.column)
            self._check_inheritance_cycle(name, parent_name, name_token.line, name_token.column)

        if not self._match(TokenKind.LBRACE):
            token = self._peek()
            raise expected_value("{", token.line, token.column)

        fields, methods, constructors = self._parse_class_members(name)
        self._classes[name] = ClassDef(
            name=name,
            parent_name=parent_name,
            fields=fields,
            methods=methods,
            constructors=constructors,
            line=name_token.line,
            column=name_token.column,
        )

    def _check_inheritance_cycle(self, name: str, parent_name: str, line: int, column: int) -> None:
        seen = {name}
        current = parent_name
        while current:
            if current in seen:
                raise inheritance_cycle(name, parent_name, line, column)
            seen.add(current)
            parent_def = self._classes.get(current)
            if parent_def is None:
                break
            current = parent_def.parent_name or ""

    def _parse_class_members(
        self,
        class_name: str,
    ) -> tuple[list[ClassField], dict[str, ClassMethod], list[ClassConstructor]]:
        previous_class_name = self._current_class_name
        self._current_class_name = class_name
        fields: list[ClassField] = []
        methods: dict[str, ClassMethod] = {}
        constructors: list[ClassConstructor] = []
        field_names: set[str] = set()
        constructor_arities: set[int] = set()

        try:
            while not self._check(TokenKind.RBRACE):
                if self._is_at_end():
                    token = self._previous()
                    raise missing_closing_brace(token.line, token.column)

                if self._check(TokenKind.SOIT):
                    self._advance()
                    field = self._parse_class_field(class_name)
                    if field.name in field_names:
                        raise duplicate_class_field(field.name, self._previous().line, self._previous().column)
                    field_names.add(field.name)
                    fields.append(field)
                    continue

                if self._match(TokenKind.CONSTRUCTEUR):
                    constructor = self._parse_class_constructor()
                    if len(constructor.params) in constructor_arities:
                        raise duplicate_class_constructor(
                            len(constructor.params),
                            constructor.line,
                            constructor.column,
                        )
                    constructor_arities.add(len(constructor.params))
                    constructors.append(constructor)
                    continue

                if self._check(TokenKind.DEFINIR):
                    self._advance()
                    if not self._match(TokenKind.FONCTION):
                        token = self._peek()
                        raise expected_fonction_or_classe(token.line, token.column)
                    method = self._parse_class_method()
                    if method.name in methods:
                        raise duplicate_class_method(method.name, method.line, method.column)
                    methods[method.name] = method
                    continue

                if self._check(TokenKind.SEMICOLON):
                    token = self._advance()
                    raise empty_statement(token.line, token.column)

                token = self._peek()
                raise unexpected_in_class(str(token.value), token.line, token.column)

            self._advance()
            return fields, methods, constructors
        finally:
            self._current_class_name = previous_class_name

    def _parse_class_constructor(self) -> ClassConstructor:
        start = self._peek()
        self._consume(TokenKind.LPAREN, expected_parameter_list)
        params = self._parse_function_parameters()
        if not self._match(TokenKind.RPAREN):
            token = self._peek()
            raise missing_closing_paren(token.line, token.column)
        if not self._match(TokenKind.LBRACE):
            token = self._peek()
            raise expected_value("{", token.line, token.column)
        body_tokens = self._skip_block_body()
        return ClassConstructor(
            params=params,
            body_tokens=body_tokens,
            line=start.line,
            column=start.column,
        )

    def _parse_class_field(self, class_name: str) -> ClassField:
        var_type = self._parse_type()
        name_token = self._consume_variable_name()
        name = str(name_token.value)
        if self._match(TokenKind.EQUAL):
            if self._check(TokenKind.SEMICOLON):
                token = self._peek()
                raise missing_value_after_equal(name, token.line, token.column)
            value = self._value_for_type(var_type, name, name_token.line, name_token.column)
        else:
            value = default_value_for_type(var_type)
        self._consume_semicolon()
        self._check_value_type(name, var_type, value, name_token.line, name_token.column)
        return ClassField(name=name, var_type=var_type, default_value=value)

    def _parse_class_method(self) -> ClassMethod:
        name_token = self._consume_function_name()
        name = str(name_token.value)
        self._consume(TokenKind.LPAREN, expected_parameter_list)
        params = self._parse_function_parameters()
        if not self._match(TokenKind.RPAREN):
            token = self._peek()
            raise missing_closing_paren(token.line, token.column)
        if not self._match(TokenKind.LBRACE):
            token = self._peek()
            raise expected_value("{", token.line, token.column)
        body_tokens = self._skip_block_body()
        return_type: TypeSpec | None = None
        if self._match(TokenKind.RETOURNE):
            return_type = self._parse_type()
        return ClassMethod(
            name=name,
            params=params,
            return_type=return_type,
            body_tokens=body_tokens,
            line=name_token.line,
            column=name_token.column,
        )

    def _execute_constructor(
        self,
        instance: UserInstance,
        constructor: ClassConstructor,
        arg_values: list[Value],
        line: int,
        column: int,
    ) -> None:
        if len(arg_values) != len(constructor.params):
            raise wrong_function_argument_count(
                "constructeur",
                len(constructor.params),
                len(arg_values),
                line,
                column,
            )

        saved_position = self._position
        outer_tokens = self._tokens
        self._tokens = constructor.body_tokens
        self._position = 0
        self._push_scope()
        try:
            scope = self._current_scope()
            for field_name, variable in instance.fields.items():
                scope[field_name] = variable
            for param, arg in zip(constructor.params, arg_values, strict=True):
                if is_pointer_type(param.var_type):
                    assert isinstance(arg, Pointer)
                    target_type = pointer_target_type(param.var_type)
                    assert target_type is not None
                    self._check_pointer_target_type(
                        param.name,
                        target_type,
                        arg,
                        line,
                        column,
                    )
                    scope[param.name] = Variable(param.var_type, arg.copy())
                else:
                    assert not isinstance(arg, Pointer)
                    value = self._coerce_argument(param.var_type, arg)
                    value = (
                        copy_value(value)
                        if isinstance(param.var_type, VarType) and is_object_var_type(param.var_type)
                        else value
                    )
                    self._check_value_type(param.name, param.var_type, value, line, column)
                    scope[param.name] = Variable(param.var_type, value)
            while self._position < len(self._tokens):
                self._block_statement(None)
        finally:
            self._tokens = outer_tokens
            self._position = saved_position
            self._pop_scope()

    def _coerce_argument(self, var_type: TypeSpec, value: Value) -> Value:
        if isinstance(var_type, VarType) and var_type == VarType.MOTS and isinstance(value, str):
            return Mots(value)
        return value

    def _parse_nouveau(self) -> Value:
        start = self._peek()
        self._advance()
        type_token = self._consume_nouveau_type_name()
        type_name = str(type_token.value)
        self._consume(TokenKind.LPAREN, expected_parameter_list)

        if is_object_type(type_name):
            obj = create_object(type_name)
            if type_name == "Carnet":
                entries = self._parse_carnet_constructor_args()
                if not self._match(TokenKind.RPAREN):
                    token = self._peek()
                    raise missing_closing_paren(token.line, token.column)
                return fill_carnet_object(obj, entries, type_token.line, type_token.column)  # type: ignore[arg-type]
            args = self._parse_value_arguments()
            if not self._match(TokenKind.RPAREN):
                token = self._peek()
                raise missing_closing_paren(token.line, token.column)
            if type_name == "Mots":
                return fill_mots_object(obj, args, type_token.line, type_token.column)
            return fill_list_object(obj, args, type_token.line, type_token.column)

        if type_name in self._classes:
            args = self._parse_value_arguments()
            if not self._match(TokenKind.RPAREN):
                token = self._peek()
                raise missing_closing_paren(token.line, token.column)
            return instantiate_class(
                self,
                self._classes[type_name],
                self._classes,
                args,
                line=type_token.line,
                column=type_token.column,
            )

        raise undefined_class(type_name, type_token.line, type_token.column)

    def _consume_nouveau_type_name(self) -> Token:
        if self._check(TokenKind.TYPE) and is_object_type(str(self._peek().value)):
            return self._advance()
        if self._check(TokenKind.IDENTIFIER):
            token = self._advance()
            name = str(token.value)
            if name in self._classes:
                return token
            legacy = legacy_object_type_name(name)
            if legacy is not None:
                raise use_nouveau_to_create(legacy.value, token.line, token.column)
            if not is_capitalized_type_name(name):
                raise object_name_needs_capital(name, token.line, token.column)
            raise undefined_class(name, token.line, token.column)
        token = self._peek()
        raise expected_type_after_nouveau(token.line, token.column)

    def _parse_value_arguments(self) -> list[Value]:
        args: list[Value] = []
        if self._check(TokenKind.RPAREN):
            return args

        while True:
            args.append(self._value_expression())
            if not self._match(TokenKind.COMMA):
                break

        return args

    def _parse_carnet_constructor_args(self) -> dict[str, Value]:
        entries: dict[str, Value] = {}
        if self._check(TokenKind.RPAREN):
            return entries

        while True:
            key_token = self._consume(TokenKind.IDENTIFIER, expected_variable_name)
            key = str(key_token.value)
            self._consume(TokenKind.COLON, expected_value)
            value = self._value_expression()
            entries[key] = value
            if not self._match(TokenKind.COMMA):
                break

        return entries

    def _ensure_capitalized_type_name(self, name: str, line: int, column: int) -> None:
        if not is_capitalized_type_name(name):
            raise object_name_needs_capital(name, line, column)

    def _call_instance_method(
        self,
        instance: UserInstance,
        method_name: str,
        args: list[Value],
        line: int,
        column: int,
    ) -> Value | None:
        class_def = self._classes[instance.class_name]
        method = class_def.resolve_method(method_name, self._classes)
        if method is None:
            raise unknown_instance_method(instance.class_name, method_name, line, column)

        if len(args) != len(method.params):
            raise wrong_function_argument_count(
                method_name,
                len(method.params),
                len(args),
                line,
                column,
            )

        if method.builtin_handler == "afficher":
            self.output.append(instance.describe())
            return None

        if method.builtin_handler == "equals":
            other = args[0]
            if not isinstance(other, UserInstance):
                return False
            return instances_equal(instance, other)

        saved_position = self._position
        self._push_scope()
        try:
            scope = self._current_scope()
            for field_name, variable in instance.fields.items():
                scope[field_name] = variable
            for param, arg in zip(method.params, args, strict=True):
                if is_pointer_type(param.var_type):
                    assert isinstance(arg, Pointer)
                    target_type = pointer_target_type(param.var_type)
                    assert target_type is not None
                    self._check_pointer_target_type(
                        param.name,
                        target_type,
                        arg,
                        line,
                        column,
                    )
                    scope[param.name] = Variable(param.var_type, arg.copy())
                else:
                    assert not isinstance(arg, Pointer)
                    value = self._coerce_argument(param.var_type, arg)
                    value = (
                        copy_value(value)
                        if isinstance(param.var_type, VarType) and is_object_var_type(param.var_type)
                        else value
                    )
                    self._check_value_type(param.name, param.var_type, value, line, column)
                    scope[param.name] = Variable(param.var_type, value)
            return self._execute_method_body(method)
        finally:
            self._position = saved_position
            self._pop_scope()

    def _execute_method_body(self, method: ClassMethod) -> Value:
        outer_tokens = self._tokens
        self._tokens = method.body_tokens
        self._position = 0
        context = (method.return_type, method.name, method.line, method.column)

        try:
            while self._position < len(self._tokens):
                self._block_statement(context)
        except ReturnSignal as signal:
            if method.return_type is None:
                return None  # type: ignore[return-value]
            return signal.value  # type: ignore[return-value]
        finally:
            self._tokens = outer_tokens

        if method.return_type is not None:
            raise missing_return_statement(format_type_name(method.return_type), method.line, method.column)

        return None  # type: ignore[return-value]

    def _parse_function_parameters(self) -> list[Parameter]:
        params: list[Parameter] = []
        if self._check(TokenKind.RPAREN):
            return params

        while True:
            var_type = self._parse_type()
            name_token = self._consume_variable_name()
            name = str(name_token.value)
            params.append(Parameter(name=name, var_type=var_type))

            if not self._match(TokenKind.COMMA):
                break

        return params

    def _skip_block_body(self) -> list[Token]:
        body_start = self._position
        depth = 1

        while depth > 0:
            if self._is_at_end():
                token = self._previous()
                raise missing_closing_brace(token.line, token.column)

            if self._check(TokenKind.LBRACE):
                depth += 1
            elif self._check(TokenKind.RBRACE):
                depth -= 1
                if depth == 0:
                    body_end = self._position
                    self._advance()
                    return self._tokens[body_start:body_end]

            self._advance()

        token = self._previous()
        raise missing_closing_brace(token.line, token.column)

    def _call_user_function(self, name_token: Token) -> Value:
        name = str(name_token.value)
        if name not in self._functions:
            raise undefined_function(name, name_token.line, name_token.column)

        func = self._functions[name]
        self._advance()
        self._consume(TokenKind.LPAREN, expected_parameter_list)
        arg_values = self._parse_function_arguments(func)
        if not self._match(TokenKind.RPAREN):
            token = self._peek()
            raise missing_closing_paren(token.line, token.column)

        if len(arg_values) != len(func.params):
            raise wrong_function_argument_count(
                name,
                len(func.params),
                len(arg_values),
                name_token.line,
                name_token.column,
            )

        saved_position = self._position
        self._push_scope()
        try:
            self._bind_function_parameters(func, arg_values, name_token.line, name_token.column)
            return self._execute_function_body(func)
        finally:
            self._position = saved_position
            self._pop_scope()

    def _parse_function_arguments(self, func: UserFunction) -> list[Value | Pointer]:
        args: list[Value | Pointer] = []
        if self._check(TokenKind.RPAREN):
            return args

        while True:
            if len(args) >= len(func.params):
                token = self._peek()
                raise wrong_function_argument_count(
                    func.name,
                    len(func.params),
                    len(args) + 1,
                    token.line,
                    token.column,
                )

            param = func.params[len(args)]
            args.append(
                self._expression_for_type(
                    param.var_type,
                    param.name,
                    func.line,
                    func.column,
                )
            )

            if not self._match(TokenKind.COMMA):
                break

        return args

    def _bind_function_parameters(
        self,
        func: UserFunction,
        arg_values: list[Value | Pointer],
        line: int,
        column: int,
    ) -> None:
        scope = self._current_scope()
        for param, arg in zip(func.params, arg_values, strict=True):
            if is_pointer_type(param.var_type):
                assert isinstance(arg, Pointer)
                target_type = pointer_target_type(param.var_type)
                assert target_type is not None
                self._check_pointer_target_type(
                    param.name,
                    target_type,
                    arg,
                    line,
                    column,
                )
                scope[param.name] = Variable(param.var_type, arg.copy())
            else:
                assert not isinstance(arg, Pointer)
                assert isinstance(param.var_type, VarType)
                value = self._coerce_argument(param.var_type, arg)
                value = copy_value(value) if is_object_var_type(param.var_type) else value
                self._check_value_type(param.name, param.var_type, value, line, column)
                scope[param.name] = Variable(param.var_type, value)

    def _execute_function_body(self, func: UserFunction) -> Value:
        outer_tokens = self._tokens
        self._tokens = func.body_tokens
        self._position = 0
        context = (func.return_type, func.name, func.line, func.column)

        try:
            while self._position < len(self._tokens):
                self._block_statement(context)
        except ReturnSignal as signal:
            if func.return_type is None:
                return None  # type: ignore[return-value]
            return signal.value  # type: ignore[return-value]
        finally:
            self._tokens = outer_tokens

        if func.return_type is not None:
            raise missing_return_statement(format_type_name(func.return_type), func.line, func.column)

        return None  # type: ignore[return-value]

    def _block_statement(
        self,
        function_context: tuple[TypeSpec | None, str, int, int] | None = None,
    ) -> None:
        if self._check(TokenKind.SEMICOLON):
            token = self._advance()
            raise empty_statement(token.line, token.column)

        if self._check(TokenKind.SOIT):
            self._advance()
            self._declaration()
            return

        if self._check(TokenKind.AFFICHER):
            self._advance()
            self._afficher()
            return

        if self._check(TokenKind.SI):
            self._advance()
            self._if_statement(function_context)
            return

        if self._check(TokenKind.TANT):
            self._advance()
            self._while_statement(function_context)
            return

        if self._check(TokenKind.RETOURNE):
            if function_context is None:
                token = self._peek()
                raise return_outside_function(token.line, token.column)
            return_type, name, line, column = function_context
            self._return_statement(return_type, name, line, column)
            return

        if self._check(TokenKind.IDENTIFIER) and str(self._peek().value) == "valeur":
            if self._peek_next().kind == TokenKind.LPAREN and self._is_valeur_assignment():
                self._pointer_assignment()
                return

        if self._check(TokenKind.IDENTIFIER) and self._peek_next().kind == TokenKind.EQUAL:
            self._assignment()
            return

        self._statement_expression()
        self._consume_semicolon()

    def _return_statement(
        self,
        return_type: TypeSpec | None,
        name: str,
        line: int,
        column: int,
    ) -> None:
        token = self._peek()
        self._advance()
        if return_type is None:
            raise return_in_void_function(token.line, token.column)

        value = self._expression_for_type(return_type, name, line, column)
        self._consume_semicolon()
        self._check_value_type(name, return_type, value, self._previous().line, self._previous().column)
        raise ReturnSignal(value)

    def _if_statement(
        self,
        function_context: tuple[TypeSpec | None, str, int, int] | None = None,
    ) -> None:
        condition = self._logique_condition()
        if condition:
            self._execute_block(function_context)
            return

        self._skip_block()
        if self._match(TokenKind.SINON):
            self._execute_block(function_context)

    def _while_statement(
        self,
        function_context: tuple[TypeSpec | None, str, int, int] | None = None,
    ) -> None:
        start = self._position
        while True:
            self._position = start
            if not self._logique_condition():
                self._skip_block()
                return
            self._execute_block(function_context)

    def _execute_block(
        self,
        function_context: tuple[TypeSpec | None, str, int, int] | None = None,
    ) -> None:
        if not self._match(TokenKind.LBRACE):
            token = self._peek()
            raise expected_value("{", token.line, token.column)

        while not self._check(TokenKind.RBRACE):
            if self._is_at_end():
                token = self._previous()
                raise missing_closing_brace(token.line, token.column)
            self._block_statement(function_context)

        self._advance()

    def _skip_block(self) -> None:
        if not self._match(TokenKind.LBRACE):
            token = self._peek()
            raise expected_value("{", token.line, token.column)

        depth = 1
        while depth > 0:
            if self._is_at_end():
                token = self._previous()
                raise missing_closing_brace(token.line, token.column)

            if self._check(TokenKind.LBRACE):
                depth += 1
            elif self._check(TokenKind.RBRACE):
                depth -= 1
                if depth == 0:
                    self._advance()
                    return

            self._advance()

    def _logique_condition(self) -> bool:
        if self._check(TokenKind.IDENTIFIER) and self._peek_next().kind == TokenKind.LPAREN:
            name_token = self._peek()
            value = self._call_user_function(name_token)
            if not isinstance(value, bool):
                raise type_mismatch(
                    "condition",
                    VarType.LOGIQUE.value,
                    self._value_type_name(value),
                    name_token.line,
                    name_token.column,
                )
            return value

        if self._check(TokenKind.VRAI) or self._check(TokenKind.FAUX):
            return self._logique_literal()

        if self._can_start_value_expression():
            start = self._position
            left = self._value_expression()
            if self._match(TokenKind.EQEQ, TokenKind.NEQ):
                operator = self._previous()
                right = self._value_expression()
                equal = values_equal(left, right)
                return equal if operator.kind == TokenKind.EQEQ else not equal
            if isinstance(left, bool):
                return left
            self._position = start

        start = self._position
        if self._can_start_numeric_expression():
            left = self._numeric_expression()
            if self._match(
                TokenKind.EQEQ,
                TokenKind.NEQ,
                TokenKind.LT,
                TokenKind.GT,
                TokenKind.LTE,
                TokenKind.GTE,
            ):
                operator = self._previous()
                right = self._numeric_expression()
                return self._evaluate_comparison(left, operator.kind, right)
            self._position = start

        if self._check(TokenKind.IDENTIFIER):
            token = self._advance()
            value = self._lookup_variable(token)
            if is_nothing(value):
                raise nothing_value_not_allowed(str(token.value), token.line, token.column)
            if not isinstance(value, bool):
                raise type_mismatch(
                    str(token.value),
                    VarType.LOGIQUE.value,
                    self._value_type_name(value),
                    token.line,
                    token.column,
                )
            return value

        token = self._peek()
        raise expected_logique_condition(token.line, token.column)

    def _can_start_value_expression(self) -> bool:
        if self._check(TokenKind.NUMBER):
            return True
        if self._check(TokenKind.TEXT):
            return True
        if self._check(TokenKind.NOUVEAU):
            return True
        if self._check(TokenKind.RIEN):
            return True
        if self._check(TokenKind.VRAI) or self._check(TokenKind.FAUX):
            return True
        if self._check(TokenKind.TYPE) and is_object_type(str(self._peek().value)):
            return True
        if self._check(TokenKind.IDENTIFIER):
            return True
        return False

    def _can_start_numeric_expression(self) -> bool:
        if (
            self._check(TokenKind.NUMBER)
            or self._check(TokenKind.MINUS)
            or self._check(TokenKind.LPAREN)
        ):
            return True
        if self._check(TokenKind.IDENTIFIER):
            if self._peek_next().kind == TokenKind.LPAREN:
                return True
            variable = self._lookup_variable_entry(
                str(self._peek().value),
                self._peek().line,
                self._peek().column,
            )
            return isinstance(variable.var_type, VarType) and variable.var_type == VarType.NOMBRE
        return False

    def _evaluate_comparison(self, left: float | int, operator: TokenKind, right: float | int) -> bool:
        match operator:
            case TokenKind.EQEQ:
                return left == right
            case TokenKind.NEQ:
                return left != right
            case TokenKind.LT:
                return left < right
            case TokenKind.GT:
                return left > right
            case TokenKind.LTE:
                return left <= right
            case TokenKind.GTE:
                return left >= right
            case _:
                raise AssertionError(f"Opérateur de comparaison inattendu : {operator}")

    def _is_valeur_assignment(self) -> bool:
        position = self._position
        try:
            self._advance()
            if not self._match(TokenKind.LPAREN):
                return False
            self._parse_pointer_operand()
            if not self._match(TokenKind.RPAREN):
                return False
            return self._check(TokenKind.EQUAL)
        finally:
            self._position = position

    def _assignment(self) -> None:
        if self._check(TokenKind.IDENTIFIER) and str(self._peek().value) == "valeur":
            self._pointer_assignment()
            return

        name_token = self._consume(TokenKind.IDENTIFIER, expected_variable_name)
        name = str(name_token.value)
        variable = self._lookup_variable_entry_for_assignment(name, name_token.line, name_token.column)
        self._consume(TokenKind.EQUAL, expected_equal)
        value = self._expression_for_type(
            variable.var_type,
            name,
            name_token.line,
            name_token.column,
        )
        self._consume_semicolon()
        self._check_value_type(name, variable.var_type, value, name_token.line, name_token.column)
        variable.value = value

    def _pointer_assignment(self) -> None:
        token = self._peek()
        self._advance()
        self._consume(TokenKind.LPAREN, expected_value)
        pointer = self._parse_pointer_operand()
        if not self._match(TokenKind.RPAREN):
            peek = self._peek()
            raise missing_closing_paren(peek.line, peek.column)

        target_type = pointer.target.var_type
        if is_pointer_type(target_type):
            raise pointer_type_mismatch(
                "valeur",
                format_type_name(target_type),
                "valeur",
                token.line,
                token.column,
            )

        assert isinstance(target_type, VarType)
        self._consume(TokenKind.EQUAL, expected_equal)
        value = self._expression_for_type(target_type, "valeur", token.line, token.column)
        self._consume_semicolon()
        self._check_value_type("valeur", target_type, value, token.line, token.column)
        pointer.target.value = value

    def _expression_for_type(self, var_type: TypeSpec, name: str, line: int, column: int) -> Value | Pointer:
        if is_pointer_type(var_type):
            return self._pointer_expression(var_type, name, line, column)
        assert isinstance(var_type, VarType)
        if var_type == VarType.NOMBRE:
            return self._numeric_expression()
        if var_type == VarType.MOTS:
            return self._mots_expression(name, line, column)
        if var_type == VarType.LOGIQUE:
            return self._logique_expression(name, line, column)
        return self._value_expression()

    def _current_scope(self) -> dict[str, Variable]:
        return self._scopes[-1]

    def _push_scope(self) -> None:
        self._scopes.append({})

    def _pop_scope(self) -> None:
        self._scopes.pop()

    def _lookup_variable_entry(self, name: str, line: int, column: int) -> Variable:
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        raise undefined_variable(name, line, column)

    def _lookup_variable_entry_for_assignment(self, name: str, line: int, column: int) -> Variable:
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        raise assign_to_undefined(name, line, column)

    def _consume_variable_name(self) -> Token:
        token = self._peek()
        if token.kind == TokenKind.TYPE:
            raise type_as_variable_name(str(token.value), token.line, token.column)
        return self._consume(TokenKind.IDENTIFIER, expected_variable_name)

    def _consume_function_name(self) -> Token:
        if self._check(TokenKind.IDENTIFIER) or self._check(TokenKind.AFFICHER):
            token = self._advance()
            if token.kind == TokenKind.AFFICHER:
                return Token(TokenKind.IDENTIFIER, "afficher", token.line, token.column)
            return token
        token = self._peek()
        raise expected_function_name(token.line, token.column)

    def _parse_type(self) -> TypeSpec:
        token = self._peek()
        if token.kind == TokenKind.IDENTIFIER:
            name = str(token.value)
            legacy = legacy_object_type_name(name)
            if legacy is not None and name != "mots":
                raise use_nouveau_to_create(legacy.value, token.line, token.column)
            if legacy is not None:
                self._advance()
                return legacy
            if name in self._classes or name == self._current_class_name:
                self._advance()
                return ClassType(name)
            if is_capitalized_type_name(name):
                raise undefined_class(name, token.line, token.column)
            raise expected_type(token.line, token.column, found=name)
        if token.kind != TokenKind.TYPE:
            raise expected_type(token.line, token.column)

        type_name = str(self._advance().value)
        if type_name == "pointeur":
            inner_token = self._peek()
            if inner_token.kind != TokenKind.TYPE:
                raise expected_type_after_pointeur(inner_token.line, inner_token.column)
            inner_name = str(self._advance().value)
            if inner_name == "pointeur":
                raise nested_pointer_not_allowed(inner_token.line, inner_token.column)
            inner_type = parse_type_name(inner_name)
            if inner_type is None:
                raise expected_type_after_pointeur(inner_token.line, inner_token.column)
            return PointerType(inner_type)

        var_type = parse_type_name(type_name)
        if var_type is None:
            raise expected_type(token.line, token.column)
        return var_type

    def _parse_adresse_call(self) -> Pointer:
        token = self._peek()
        self._advance()
        self._consume(TokenKind.LPAREN, expected_value)
        if not self._check(TokenKind.IDENTIFIER):
            peek = self._peek()
            raise adresse_requires_variable(peek.line, peek.column)
        name_token = self._advance()
        if not self._match(TokenKind.RPAREN):
            peek = self._peek()
            raise missing_closing_paren(peek.line, peek.column)

        variable = self._lookup_variable_entry(str(name_token.value), name_token.line, name_token.column)
        return Pointer(target=variable, target_name=str(name_token.value))

    def _parse_valeur_call(self) -> Value:
        self._advance()
        self._consume(TokenKind.LPAREN, expected_value)
        pointer = self._parse_pointer_operand()
        if not self._match(TokenKind.RPAREN):
            peek = self._peek()
            raise missing_closing_paren(peek.line, peek.column)
        return pointer.target.value

    def _parse_type_call(self) -> str:
        start = self._peek()
        self._advance()
        self._consume(TokenKind.LPAREN, expected_value)
        if self._check(TokenKind.RPAREN):
            raise type_requires_argument(start.line, start.column)

        type_name = self._type_name_from_argument()

        if self._match(TokenKind.COMMA):
            raise type_wrong_argument_count(start.line, start.column)
        if not self._match(TokenKind.RPAREN):
            peek = self._peek()
            raise missing_closing_paren(peek.line, peek.column)
        return type_name

    def _type_name_from_argument(self) -> str:
        if self._check(TokenKind.IDENTIFIER):
            next_kind = self._peek_next().kind
            name = str(self._peek().value)
            if name == "adresse" and next_kind == TokenKind.LPAREN:
                pointer = self._parse_adresse_call()
                return self._value_type_name(pointer)
            if next_kind not in (TokenKind.LPAREN, TokenKind.DOT):
                token = self._advance()
                variable = self._lookup_variable_entry(str(token.value), token.line, token.column)
                return format_type_name(variable.var_type)

        value = self._value_expression()
        return self._value_type_name(value)

    def _parse_pointer_operand(self) -> Pointer:
        if self._check(TokenKind.IDENTIFIER) and str(self._peek().value) == "adresse":
            return self._parse_adresse_call()

        name_token = self._consume(TokenKind.IDENTIFIER, expected_variable_name)
        name = str(name_token.value)
        variable = self._lookup_variable_entry(name, name_token.line, name_token.column)
        if is_nothing(variable.value):
            raise not_a_pointer(name, name_token.line, name_token.column)
        if not isinstance(variable.value, Pointer):
            raise not_a_pointer(name, name_token.line, name_token.column)
        return variable.value

    def _pointer_expression(
        self,
        pointer_type: PointerType,
        name: str,
        line: int,
        column: int,
    ) -> Value | Pointer:
        if self._check(TokenKind.RIEN):
            self._advance()
            return NOTHING

        if self._check(TokenKind.IDENTIFIER) and str(self._peek().value) == "adresse":
            pointer = self._parse_adresse_call()
            self._check_pointer_target_type(name, pointer_type.target, pointer, line, column)
            return pointer

        if self._check(TokenKind.IDENTIFIER):
            var_name = str(self._peek().value)
            variable = self._lookup_variable_entry(var_name, self._peek().line, self._peek().column)
            if is_pointer_type(variable.var_type) and isinstance(variable.value, Pointer):
                self._advance()
                self._check_pointer_target_type(name, pointer_type.target, variable.value, line, column)
                return variable.value.copy()

        token = self._peek()
        raise type_mismatch(name, pointer_type.value, str(token.value), line, column)

    def _check_pointer_target_type(
        self,
        name: str,
        expected_target: VarType,
        pointer: Pointer,
        line: int,
        column: int,
    ) -> None:
        target_type = pointer.target.var_type
        if is_pointer_type(target_type):
            raise pointer_type_mismatch(
                name,
                expected_target.value,
                format_type_name(target_type),
                line,
                column,
            )
        assert isinstance(target_type, VarType)
        if target_type != expected_target:
            raise pointer_type_mismatch(name, expected_target.value, target_type.value, line, column)

    def _try_builtin_call(self) -> Value | Pointer | None:
        if not self._check(TokenKind.IDENTIFIER) or self._peek_next().kind != TokenKind.LPAREN:
            return None

        name = str(self._peek().value)
        if name == "adresse":
            return self._parse_adresse_call()
        if name == "valeur":
            return self._parse_valeur_call()
        if name == "type":
            return self._parse_type_call()
        return None

    def _rien_for_type(self, var_type: TypeSpec, name: str, line: int, column: int) -> Value:
        self._advance()
        if is_pointer_type(var_type):
            return NOTHING
        if isinstance(var_type, VarType) and is_primitive_var_type(var_type):
            return NOTHING
        raise rien_not_allowed_for_type(format_type_name(var_type), line, column)

    def _value_for_type(self, var_type: TypeSpec, name: str, line: int, column: int) -> Value | Pointer:
        if self._check(TokenKind.RIEN):
            return self._rien_for_type(var_type, name, self._peek().line, self._peek().column)

        if is_pointer_type(var_type):
            return self._pointer_expression(var_type, name, line, column)

        if is_class_type(var_type):
            if self._check(TokenKind.NOUVEAU):
                value = self._parse_nouveau()
                if not isinstance(value, UserInstance) or value.class_name != var_type.name:
                    raise type_mismatch(name, var_type.name, self._value_type_name(value), line, column)
                return value
            if (
                self._check(TokenKind.IDENTIFIER)
                and str(self._peek().value) == var_type.name
                and self._peek_next().kind == TokenKind.LPAREN
            ):
                token = self._peek()
                raise use_nouveau_to_create(var_type.name, token.line, token.column)
            token = self._peek()
            raise use_nouveau_to_create(var_type.name, token.line, token.column)

        assert isinstance(var_type, VarType)
        if is_object_var_type(var_type):
            if var_type == VarType.MOTS and self._check(TokenKind.TEXT):
                return Mots(str(self._advance().value))
            if self._check(TokenKind.NOUVEAU):
                value = self._parse_nouveau()
                if not isinstance(value, FrLangObject) or value.type_name != var_type.value:
                    raise type_mismatch(name, var_type.value, self._value_type_name(value), line, column)
                return value
            if self._check(TokenKind.TYPE) and self._peek_next().kind == TokenKind.LBRACKET:
                token = self._peek()
                raise deprecated_object_literal_syntax(str(token.value), token.line, token.column)
            if self._check(TokenKind.IDENTIFIER) or self._check(TokenKind.NUMBER) or self._check(TokenKind.TEXT):
                value = self._value_expression()
                if not isinstance(value, FrLangObject) or value.type_name != var_type.value:
                    raise type_mismatch(name, var_type.value, self._value_type_name(value), line, column)
                return value
            raise use_nouveau_to_create(var_type.value, line, column)

        if var_type == VarType.LOGIQUE:
            if self._check(TokenKind.NUMBER):
                token = self._peek()
                raise type_mismatch(
                    name,
                    var_type.value,
                    VarType.NOMBRE.value,
                    token.line,
                    token.column,
                )
            if self._check(TokenKind.TEXT):
                token = self._peek()
                raise type_mismatch(
                    name,
                    var_type.value,
                    VarType.MOTS.value,
                    token.line,
                    token.column,
                )
            return self._logique_expression(name, line, column)

        return self._numeric_expression()

    def _literal_value(self) -> Value:
        if self._check(TokenKind.NUMBER):
            return self._advance().value  # type: ignore[return-value]
        if self._check(TokenKind.TEXT):
            return str(self._advance().value)
        if self._check(TokenKind.VRAI) or self._check(TokenKind.FAUX):
            return self._logique_literal()
        if self._check(TokenKind.NOUVEAU):
            return self._parse_nouveau()
        if self._check(TokenKind.TYPE) and is_object_type(str(self._peek().value)):
            token = self._peek()
            if self._peek_next().kind == TokenKind.LBRACKET:
                raise deprecated_object_literal_syntax(str(token.value), token.line, token.column)
            raise use_nouveau_to_create(str(token.value), token.line, token.column)
        token = self._peek()
        raise expected_value(str(token.value), token.line, token.column)

    def _statement_expression(self) -> Value:
        if self._check(TokenKind.TEXT):
            return str(self._advance().value)

        if self._check(TokenKind.VRAI) or self._check(TokenKind.FAUX):
            return self._logique_literal()

        if self._check(TokenKind.IDENTIFIER):
            if self._peek_next().kind == TokenKind.LPAREN:
                name = str(self._peek().value)
                if name in {"adresse", "valeur", "type"}:
                    return self._value_expression()
                if name in self._classes:
                    token = self._peek()
                    raise use_nouveau_to_create(name, token.line, token.column)
                if name in self._functions and self._functions[name].return_type is None:
                    return self._call_user_function(self._peek())
            if self._peek_next().kind == TokenKind.SEMICOLON:
                token = self._advance()
                variable = self._lookup_variable_entry(str(token.value), token.line, token.column)
                if isinstance(variable.value, Pointer):
                    raise pointer_requires_valeur(str(token.value), token.line, token.column)
                return variable.value
            if self._peek_next().kind == TokenKind.DOT:
                value = self._value_expression()
                return value

        if self._check(TokenKind.NOUVEAU):
            return self._value_expression()

        if self._check(TokenKind.TYPE) and is_object_type(str(self._peek().value)):
            return self._value_expression()

        return self._numeric_expression()

    def _display_expression(self) -> Value | Pointer:
        if self._check(TokenKind.IDENTIFIER) and str(self._peek().value) == "adresse":
            if self._peek_next().kind == TokenKind.LPAREN:
                return self._parse_adresse_call()

        if self._check(TokenKind.IDENTIFIER):
            if self._peek_next().kind not in (TokenKind.LPAREN, TokenKind.DOT):
                token = self._peek()
                variable = self._lookup_variable_entry(str(token.value), token.line, token.column)
                if isinstance(variable.value, Pointer):
                    self._advance()
                    return variable.value

        if self._check(TokenKind.TEXT):
            return str(self._advance().value)

        if self._check(TokenKind.VRAI) or self._check(TokenKind.FAUX):
            return self._logique_literal()

        if self._check(TokenKind.IDENTIFIER) and str(self._peek().value) == "valeur":
            if self._peek_next().kind == TokenKind.LPAREN:
                return self._parse_valeur_call()

        if self._check(TokenKind.IDENTIFIER) or (
            self._check(TokenKind.TYPE) and is_object_type(str(self._peek().value))
        ):
            return self._value_expression()

        return self._numeric_expression()

    def _value_expression(self) -> Value:
        value = self._primary_value()
        return self._postfix_methods(value)

    def _primary_value(self) -> Value:
        builtin = self._try_builtin_call()
        if builtin is not None:
            if isinstance(builtin, Pointer):
                token = self._previous()
                raise pointer_operation_not_allowed(token.line, token.column)
            return builtin

        if self._check(TokenKind.NOUVEAU):
            return self._parse_nouveau()

        if self._check(TokenKind.TYPE) and is_object_type(str(self._peek().value)):
            token = self._peek()
            if self._peek_next().kind == TokenKind.LBRACKET:
                raise deprecated_object_literal_syntax(str(token.value), token.line, token.column)
            raise use_nouveau_to_create(str(token.value), token.line, token.column)

        if self._match(TokenKind.NUMBER):
            return self._previous().value  # type: ignore[return-value]

        if self._match(TokenKind.TEXT):
            return str(self._previous().value)

        if self._check(TokenKind.VRAI) or self._check(TokenKind.FAUX):
            return self._logique_literal()

        if self._match(TokenKind.RIEN):
            return NOTHING

        if self._check(TokenKind.IDENTIFIER) and self._peek_next().kind == TokenKind.LPAREN:
            name = str(self._peek().value)
            if name in self._classes:
                token = self._peek()
                raise use_nouveau_to_create(name, token.line, token.column)
            return self._call_user_function(self._peek())

        if self._match(TokenKind.IDENTIFIER):
            token = self._previous()
            variable = self._lookup_variable_entry(str(token.value), token.line, token.column)
            if isinstance(variable.value, Pointer):
                raise pointer_requires_valeur(str(token.value), token.line, token.column)
            return variable.value

        token = self._peek()
        raise expected_value(str(token.value), token.line, token.column)

    def _postfix_methods(self, value: Value) -> Value:
        while self._match(TokenKind.DOT):
            if isinstance(value, Pointer):
                token = self._previous()
                raise pointer_operation_not_allowed(token.line, token.column)

            if not isinstance(value, FrLangObject):
                token = self._previous()
                raise object_in_numeric_expression(
                    self._value_type_name(value),
                    token.line,
                    token.column,
                )

            method_token = self._parse_method_name_token()
            method_name = str(method_token.value)

            if self._match(TokenKind.LPAREN):
                args = self._parse_argument_list()

                if not self._match(TokenKind.RPAREN):
                    token = self._peek()
                    raise missing_closing_paren(token.line, token.column)

                result = value.call_method(
                    method_name,
                    args,
                    method_token.line,
                    method_token.column,
                )
                if result is not None:
                    value = result
            elif isinstance(value, UserInstance) and method_name in value.fields:
                field_var = value.fields[method_name]
                if isinstance(field_var.value, Pointer):
                    raise pointer_requires_valeur(method_name, method_token.line, method_token.column)
                value = field_var.value
            elif isinstance(value, UserInstance):
                raise unknown_instance_field(value.class_name, method_name, method_token.line, method_token.column)
            else:
                raise expected_method_parentheses(
                    method_name,
                    method_token.line,
                    method_token.column,
                )

        return value

    def _parse_argument_list(self) -> list[Value]:
        args: list[Value] = []
        if self._check(TokenKind.RPAREN):
            return args

        while True:
            args.append(self._value_expression())
            if not self._match(TokenKind.COMMA):
                break

        return args

    def _logique_expression(self, name: str, line: int, column: int) -> bool:
        builtin = self._try_builtin_call()
        if builtin is not None:
            if not isinstance(builtin, bool):
                token = self._previous()
                raise type_mismatch(name, VarType.LOGIQUE.value, self._value_type_name(builtin), token.line, token.column)
            return builtin

        if self._check(TokenKind.VRAI) or self._check(TokenKind.FAUX):
            return self._logique_literal()

        if self._check(TokenKind.RIEN):
            token = self._peek()
            raise nothing_value_not_allowed("rien", token.line, token.column)

        if self._check(TokenKind.IDENTIFIER):
            token = self._advance()
            value = self._lookup_variable(token)
            if is_nothing(value):
                raise nothing_value_not_allowed(str(token.value), token.line, token.column)
            if not isinstance(value, bool):
                raise type_mismatch(
                    name,
                    VarType.LOGIQUE.value,
                    self._value_type_name(value),
                    token.line,
                    token.column,
                )
            return value

        token = self._peek()
        raise type_mismatch(
            name,
            VarType.LOGIQUE.value,
            str(token.value),
            token.line,
            token.column,
        )

    def _logique_literal(self) -> bool:
        if self._match(TokenKind.VRAI):
            return True
        if self._match(TokenKind.FAUX):
            return False

        token = self._peek()
        raise expected_value(str(token.value), token.line, token.column)

    def _lookup_variable(self, token: Token) -> Value | Pointer:
        name = str(token.value)
        return self._lookup_variable_entry(name, token.line, token.column).value

    def _lookup_numeric_variable(self, token: Token) -> float | int:
        name = str(token.value)
        variable = self._lookup_variable_entry(name, token.line, token.column)

        if is_pointer_type(variable.var_type) or isinstance(variable.value, Pointer):
            raise pointer_requires_valeur(name, token.line, token.column)

        if not isinstance(variable.var_type, VarType) or variable.var_type != VarType.NOMBRE:
            raise wrong_type_in_expression(format_type_name(variable.var_type), token.line, token.column)

        value = variable.value
        if is_nothing(value):
            raise nothing_value_not_allowed(name, token.line, token.column)
        if isinstance(value, FrLangObject):
            raise object_in_numeric_expression(value.type_name, token.line, token.column)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise wrong_type_in_expression(variable.var_type.value, token.line, token.column)
        return value

    def _check_value_type(self, name: str, var_type: TypeSpec, value: Value | Pointer, line: int, column: int) -> None:
        if is_pointer_type(var_type):
            if is_nothing(value):
                return
            if not isinstance(value, Pointer):
                raise type_mismatch(
                    name,
                    var_type.value,
                    self._value_type_name(value),
                    line,
                    column,
                )
            target_type = pointer_target_type(var_type)
            assert target_type is not None
            self._check_pointer_target_type(name, target_type, value, line, column)
            return

        if isinstance(value, Pointer):
            raise type_mismatch(name, format_type_name(var_type), "pointeur", line, column)

        if is_class_type(var_type):
            if var_type.name == ORIGINAL_CLASS_NAME and isinstance(value, UserInstance):
                return
            if not isinstance(value, UserInstance) or value.class_name != var_type.name:
                raise type_mismatch(
                    name,
                    var_type.name,
                    self._value_type_name(value),
                    line,
                    column,
                )
            return

        assert isinstance(var_type, VarType)
        if is_object_var_type(var_type):
            if not isinstance(value, FrLangObject) or value.type_name != var_type.value:
                raise type_mismatch(
                    name,
                    var_type.value,
                    self._value_type_name(value),
                    line,
                    column,
                )
            return

        if var_type == VarType.NOMBRE:
            if is_nothing(value):
                return
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise type_mismatch(
                    name,
                    var_type.value,
                    self._value_type_name(value),
                    line,
                    column,
                )
            return

        if var_type == VarType.LOGIQUE:
            if is_nothing(value) or isinstance(value, bool):
                return
            raise type_mismatch(
                name,
                var_type.value,
                self._value_type_name(value),
                line,
                column,
            )

    def _mots_expression(self, name: str, line: int, column: int) -> Mots:
        if self._check(TokenKind.TEXT):
            return Mots(str(self._advance().value))

        if self._check(TokenKind.NOUVEAU):
            value = self._parse_nouveau()
            if isinstance(value, Mots):
                return value
            token = self._previous()
            raise type_mismatch(name, VarType.MOTS.value, self._value_type_name(value), token.line, token.column)

        if self._check(TokenKind.IDENTIFIER):
            token = self._advance()
            value = self._lookup_variable(token)
            if isinstance(value, Mots):
                return value
            raise type_mismatch(
                str(token.value),
                VarType.MOTS.value,
                self._value_type_name(value),
                token.line,
                token.column,
            )

        token = self._peek()
        raise expected_value(str(token.value), token.line, token.column)

    def _value_type_name(self, value: Value | Pointer) -> str:
        if is_nothing(value):
            return "rien"
        if isinstance(value, Pointer):
            target_type = value.target.var_type
            if isinstance(target_type, VarType):
                return PointerType(target_type).value
            return "pointeur"
        if isinstance(value, FrLangObject):
            return value.type_name
        if isinstance(value, bool):
            return VarType.LOGIQUE.value
        if isinstance(value, str):
            return VarType.MOTS.value
        if isinstance(value, int):
            return VarType.NOMBRE.value
        if isinstance(value, float):
            return VarType.NOMBRE.value
        return "inconnu"

    def _value_type_name_from_token(self, token: Token) -> str:
        if token.kind == TokenKind.TYPE:
            return str(token.value)
        return str(token.value)

    def _parse_method_name_token(self) -> Token:
        if self._check(TokenKind.IDENTIFIER) or self._check(TokenKind.AFFICHER):
            token = self._advance()
            if token.kind == TokenKind.AFFICHER:
                return Token(TokenKind.IDENTIFIER, "afficher", token.line, token.column)
            return token
        token = self._peek()
        raise expected_method_name(token.line, token.column)

    def _consume(self, kind: TokenKind, error_factory) -> Token:
        if self._check(kind):
            return self._advance()

        token = self._peek()
        raise error_factory(token.line, token.column)

    def _consume_semicolon(self) -> None:
        if self._match(TokenKind.SEMICOLON):
            return

        token = self._peek()
        raise missing_semicolon(token.line, token.column)

    def _numeric_expression(self) -> float | int:
        value = self._term()

        while self._match(TokenKind.PLUS, TokenKind.MINUS):
            operator = self._previous()
            right = self._term()
            if operator.kind == TokenKind.PLUS:
                value = value + right
            else:
                value = value - right

        return value

    def _term(self) -> float | int:
        value = self._power()

        while self._match(TokenKind.STAR, TokenKind.SLASH, TokenKind.MOD):
            operator = self._previous()
            right = self._power()
            if operator.kind == TokenKind.STAR:
                value = value * right
            elif operator.kind == TokenKind.SLASH:
                if right == 0:
                    raise division_by_zero(operator.line, operator.column)
                value = value / right
            else:
                if right == 0:
                    raise modulo_by_zero(operator.line, operator.column)
                value = value % right

        return value

    def _power(self) -> float | int:
        value = self._unary()

        if self._match(TokenKind.CARET):
            exponent = self._power()
            value = value**exponent

        return value

    def _unary(self) -> float | int:
        if self._match(TokenKind.MINUS):
            return -self._unary()

        return self._numeric_primary()

    def _numeric_primary(self) -> float | int:
        builtin = self._try_builtin_call()
        if builtin is not None:
            if isinstance(builtin, Pointer):
                token = self._previous()
                raise pointer_operation_not_allowed(token.line, token.column)
            if isinstance(builtin, bool) or not isinstance(builtin, (int, float)):
                token = self._previous()
                raise wrong_type_in_expression(VarType.NOMBRE.value, token.line, token.column)
            return builtin

        if self._match(TokenKind.NUMBER):
            return self._previous().value  # type: ignore[return-value]

        if self._check(TokenKind.IDENTIFIER) and self._peek_next().kind == TokenKind.LPAREN:
            name_token = self._peek()
            value = self._call_user_function(name_token)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise wrong_type_in_expression(
                    VarType.NOMBRE.value,
                    name_token.line,
                    name_token.column,
                )
            return value

        if self._check(TokenKind.IDENTIFIER) and self._peek_next().kind == TokenKind.DOT:
            start = self._position
            value = self._value_expression()
            if is_nothing(value):
                token = self._tokens[start]
                raise nothing_value_not_allowed(str(token.value), token.line, token.column)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                token = self._tokens[start]
                raise wrong_type_in_expression(VarType.NOMBRE.value, token.line, token.column)
            return value

        if self._match(TokenKind.IDENTIFIER):
            return self._lookup_numeric_variable(self._previous())

        if self._match(TokenKind.LPAREN):
            value = self._numeric_expression()
            if not self._match(TokenKind.RPAREN):
                token = self._peek()
                raise missing_closing_paren(token.line, token.column)
            return value

        token = self._peek()
        if token.kind == TokenKind.EOF:
            raise incomplete_expression(token.line, token.column)

        if token.kind == TokenKind.TYPE:
            raise type_in_expression(str(token.value), token.line, token.column)

        if token.kind in (TokenKind.VRAI, TokenKind.FAUX):
            raise expected_value(str(token.value), token.line, token.column)

        raise expected_value(str(token.value), token.line, token.column)

    def _match(self, *kinds: TokenKind) -> bool:
        for kind in kinds:
            if self._check(kind):
                self._advance()
                return True
        return False

    def _check(self, kind: TokenKind) -> bool:
        if self._is_at_end():
            return False
        return self._peek().kind == kind

    def _advance(self) -> Token:
        if not self._is_at_end():
            self._position += 1
        return self._previous()

    def _peek_next(self) -> Token:
        if self._position + 1 >= len(self._tokens):
            return self._tokens[-1]
        return self._tokens[self._position + 1]

    def _is_at_end(self) -> bool:
        return self._peek().kind == TokenKind.EOF

    def _peek(self) -> Token:
        return self._tokens[self._position]

    def _previous(self) -> Token:
        return self._tokens[self._position - 1]
