from sac.functions import Parameter, UserFunction, copy_value
from sac.lexer import Lexer, Token, TokenKind
from sac.messages import (
    adresse_requires_variable,
    assign_to_undefined,
    division_by_zero,
    empty_expression,
    empty_program,
    empty_statement,
    expected_equal,
    expected_function_name,
    expected_method_name,
    expected_method_parentheses,
    expected_parameter_list,
    expected_type,
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
    not_a_pointer,
    object_in_numeric_expression,
    pointer_operation_not_allowed,
    pointer_requires_valeur,
    pointer_type_mismatch,
    return_in_void_function,
    type_as_variable_name,
    type_in_expression,
    type_mismatch,
    unexpected_symbol,
    undefined_function,
    undefined_variable,
    use_soit_for_declaration,
    variable_already_defined,
    wrong_function_argument_count,
    wrong_type_in_expression,
)
from sac.objects import Carnet, ObjetSac, Rangee, Sac, create_object, is_object_type
from sac.pointers import Pointer
from sac.types import (
    PointerType,
    TypeSpec,
    Value,
    VarType,
    format_type_name,
    format_value,
    is_object_var_type,
    is_pointer_type,
    parse_type_name,
    pointer_target_type,
)
from sac.variables import Variable


class Interpreter:
    """Interprète des expressions et de petits programmes avec variables."""

    def __init__(self, source: str) -> None:
        self._tokens = Lexer(source).tokenize()
        self._position = 0
        self._scopes: list[dict[str, Variable]] = [{}]
        self._functions: dict[str, UserFunction] = {}
        self.output: list[str] = []

    def run(self) -> Value | None:
        if self._is_at_end():
            raise empty_program()

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
                self._define_function()
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

        self._consume(TokenKind.EQUAL, expected_equal)

        if self._check(TokenKind.SEMICOLON):
            token = self._peek()
            raise missing_value_after_equal(name, token.line, token.column)

        value = self._value_for_type(var_type, name, name_token.line, name_token.column)
        if consume_semicolon:
            self._consume_semicolon()

        self._check_value_type(name, var_type, value, name_token.line, name_token.column)
        self._current_scope()[name] = Variable(var_type, value)
        return value

    def _define_function(self) -> None:
        name_token = self._consume(TokenKind.IDENTIFIER, expected_function_name)
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

        body_start, body_end = self._skip_block_body()

        return_type: TypeSpec | None = None
        if self._match(TokenKind.RETOURNE):
            return_type = self._parse_type()

        self._functions[name] = UserFunction(
            name=name,
            params=params,
            return_type=return_type,
            body_start=body_start,
            body_end=body_end,
            line=name_token.line,
            column=name_token.column,
        )

    def _parse_function_parameters(self) -> list[Parameter]:
        params: list[Parameter] = []
        if self._check(TokenKind.RPAREN):
            return params

        while True:
            name_token = self._consume_variable_name()
            name = str(name_token.value)
            self._consume(TokenKind.COLON, expected_type)
            var_type = self._parse_type()
            params.append(Parameter(name=name, var_type=var_type))

            if not self._match(TokenKind.COMMA):
                break

        return params

    def _skip_block_body(self) -> tuple[int, int]:
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
                    return body_start, body_end

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
                value = copy_value(arg) if is_object_var_type(param.var_type) else arg
                self._check_value_type(param.name, param.var_type, value, line, column)
                scope[param.name] = Variable(param.var_type, value)

    def _execute_function_body(self, func: UserFunction) -> Value:
        self._position = func.body_start
        return_value: Value | None = None
        returned = False

        while self._position < func.body_end:
            if self._check(TokenKind.RETOURNE):
                if func.return_type is None:
                    token = self._peek()
                    raise return_in_void_function(token.line, token.column)

                self._advance()
                return_value = self._expression_for_type(
                    func.return_type,
                    func.name,
                    func.line,
                    func.column,
                )
                self._consume_semicolon()
                self._check_value_type(
                    func.name,
                    func.return_type,
                    return_value,
                    self._previous().line,
                    self._previous().column,
                )
                returned = True
                self._position = func.body_end
                break

            self._block_statement()

        if func.return_type is not None and not returned:
            raise missing_return_statement(func.return_type.value, func.line, func.column)

        if func.return_type is None:
            return None  # type: ignore[return-value]

        assert return_value is not None
        return return_value

    def _block_statement(self) -> None:
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

        if self._check(TokenKind.IDENTIFIER) and str(self._peek().value) == "valeur":
            if self._peek_next().kind == TokenKind.LPAREN and self._is_valeur_assignment():
                self._pointer_assignment()
                return

        if self._check(TokenKind.IDENTIFIER) and self._peek_next().kind == TokenKind.EQUAL:
            self._assignment()
            return

        self._statement_expression()
        self._consume_semicolon()

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
            return self._text_expression()
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

    def _parse_type(self) -> TypeSpec:
        token = self._peek()
        if token.kind == TokenKind.IDENTIFIER:
            raise expected_type(token.line, token.column, found=str(token.value))
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

    def _parse_pointer_operand(self) -> Pointer:
        if self._check(TokenKind.IDENTIFIER) and str(self._peek().value) == "adresse":
            return self._parse_adresse_call()

        name_token = self._consume(TokenKind.IDENTIFIER, expected_variable_name)
        name = str(name_token.value)
        variable = self._lookup_variable_entry(name, name_token.line, name_token.column)
        if not isinstance(variable.value, Pointer):
            raise not_a_pointer(name, name_token.line, name_token.column)
        return variable.value

    def _pointer_expression(
        self,
        pointer_type: PointerType,
        name: str,
        line: int,
        column: int,
    ) -> Pointer:
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
        return None

    def _value_for_type(self, var_type: TypeSpec, name: str, line: int, column: int) -> Value | Pointer:
        if is_pointer_type(var_type):
            return self._pointer_expression(var_type, name, line, column)

        assert isinstance(var_type, VarType)
        if is_object_var_type(var_type):
            return self._parse_object_literal(var_type, name, line, column)

        if var_type == VarType.MOTS:
            if self._check(TokenKind.NUMBER):
                token = self._peek()
                raise type_mismatch(
                    name,
                    var_type.value,
                    VarType.NOMBRE.value,
                    token.line,
                    token.column,
                )
            return self._text_expression()

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

    def _parse_object_literal(
        self,
        expected_type: VarType,
        name: str,
        line: int,
        column: int,
    ) -> ObjetSac:
        token = self._peek()
        if token.kind != TokenKind.TYPE or not is_object_type(str(token.value)):
            raise type_mismatch(
                name,
                expected_type.value,
                self._value_type_name_from_token(token),
                token.line,
                token.column,
            )

        type_name = str(self._advance().value)
        actual_type = parse_type_name(type_name)
        if actual_type != expected_type:
            raise type_mismatch(name, expected_type.value, type_name, line, column)

        obj = create_object(type_name)
        self._consume(TokenKind.LBRACKET, expected_value)

        if type_name == "carnet":
            assert isinstance(obj, Carnet)
            self._parse_carnet_pairs(obj)
        else:
            self._parse_list_items(obj)

        if not self._match(TokenKind.RBRACKET):
            token = self._peek()
            raise expected_value("]", token.line, token.column)

        return obj

    def _parse_list_items(self, obj: ObjetSac) -> None:
        if self._check(TokenKind.RBRACKET):
            return

        while True:
            value = self._literal_value()
            if isinstance(obj, Rangee):
                obj.items.append(value)
            elif isinstance(obj, Sac):
                if value not in obj.items:
                    obj.items.append(value)
            elif hasattr(obj, "items"):
                obj.items.append(value)  # type: ignore[attr-defined]

            if not self._match(TokenKind.COMMA):
                break

    def _parse_carnet_pairs(self, carnet: Carnet) -> None:
        if self._check(TokenKind.RBRACKET):
            return

        while True:
            key = self._parse_carnet_key()
            key_line = self._previous().line
            key_column = self._previous().column
            self._consume(TokenKind.COLON, expected_value)
            value = self._literal_value()
            carnet._etiqueter(key, value, key_line, key_column)  # noqa: SLF001

            if not self._match(TokenKind.COMMA):
                break

    def _parse_carnet_key(self) -> str:
        if self._check(TokenKind.TEXT):
            token = self._advance()
            return str(token.value)
        if self._check(TokenKind.IDENTIFIER):
            token = self._advance()
            return str(token.value)
        token = self._peek()
        raise expected_value(str(token.value), token.line, token.column)

    def _literal_value(self) -> Value:
        if self._check(TokenKind.NUMBER):
            return self._advance().value  # type: ignore[return-value]
        if self._check(TokenKind.TEXT):
            return str(self._advance().value)
        if self._check(TokenKind.VRAI) or self._check(TokenKind.FAUX):
            return self._logique_literal()
        if self._check(TokenKind.TYPE) and is_object_type(str(self._peek().value)):
            return self._parse_object_literal(
                parse_type_name(str(self._peek().value)) or VarType.RANGEE,
                "valeur",
                self._peek().line,
                self._peek().column,
            )
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
                if name in {"adresse", "valeur"}:
                    return self._value_expression()
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

        if self._check(TokenKind.TYPE) and is_object_type(str(self._peek().value)):
            var_type = parse_type_name(str(self._peek().value))
            assert var_type is not None
            return self._parse_object_literal(
                var_type,
                "valeur",
                self._peek().line,
                self._peek().column,
            )

        if self._match(TokenKind.NUMBER):
            return self._previous().value  # type: ignore[return-value]

        if self._match(TokenKind.TEXT):
            return str(self._previous().value)

        if self._check(TokenKind.VRAI) or self._check(TokenKind.FAUX):
            return self._logique_literal()

        if self._check(TokenKind.IDENTIFIER) and self._peek_next().kind == TokenKind.LPAREN:
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

            if not isinstance(value, ObjetSac):
                token = self._previous()
                raise object_in_numeric_expression(
                    self._value_type_name(value),
                    token.line,
                    token.column,
                )

            method_token = self._consume(TokenKind.IDENTIFIER, expected_method_name)
            method_name = str(method_token.value)

            if not self._match(TokenKind.LPAREN):
                raise expected_method_parentheses(
                    method_name,
                    method_token.line,
                    method_token.column,
                )

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

        if self._check(TokenKind.IDENTIFIER):
            token = self._advance()
            value = self._lookup_variable(token)
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

    def _text_expression(self) -> str:
        builtin = self._try_builtin_call()
        if builtin is not None:
            if not isinstance(builtin, str):
                token = self._previous()
                raise type_mismatch("valeur", VarType.MOTS.value, self._value_type_name(builtin), token.line, token.column)
            return builtin

        if self._check(TokenKind.TEXT):
            return str(self._advance().value)

        if self._check(TokenKind.IDENTIFIER):
            token = self._advance()
            value = self._lookup_variable(token)
            if not isinstance(value, str):
                raise type_mismatch(
                    str(token.value),
                    VarType.MOTS.value,
                    self._value_type_name(value),
                    token.line,
                    token.column,
                )
            return value

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
        if isinstance(value, ObjetSac):
            raise object_in_numeric_expression(value.type_name, token.line, token.column)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise wrong_type_in_expression(variable.var_type.value, token.line, token.column)
        return value

    def _check_value_type(self, name: str, var_type: TypeSpec, value: Value | Pointer, line: int, column: int) -> None:
        if is_pointer_type(var_type):
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

        assert isinstance(var_type, VarType)
        if is_object_var_type(var_type):
            if not isinstance(value, ObjetSac) or value.type_name != var_type.value:
                raise type_mismatch(
                    name,
                    var_type.value,
                    self._value_type_name(value),
                    line,
                    column,
                )
            return

        if var_type == VarType.NOMBRE:
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
            if not isinstance(value, bool):
                raise type_mismatch(
                    name,
                    var_type.value,
                    self._value_type_name(value),
                    line,
                    column,
                )
            return

        if not isinstance(value, str):
            raise type_mismatch(
                name,
                var_type.value,
                self._value_type_name(value),
                line,
                column,
            )

    def _value_type_name(self, value: Value | Pointer) -> str:
        if isinstance(value, Pointer):
            target_type = value.target.var_type
            if isinstance(target_type, VarType):
                return PointerType(target_type).value
            return "pointeur"
        if isinstance(value, ObjetSac):
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
