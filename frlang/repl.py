from __future__ import annotations

import sys
from typing import TextIO

from frlang.errors import LexerError, ParseError
from frlang.interpreter import Interpreter
from frlang.types import Value, format_value

_EXIT_COMMANDS = {"quitter", "quit", "exit", "q"}
_HELP_COMMANDS = {"aide", "help", "?"}


def source_needs_continuation(source: str) -> bool:
    depth_brace = 0
    depth_paren = 0
    in_string = False
    escape = False

    index = 0
    while index < len(source):
        char = source[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth_brace += 1
        elif char == "}":
            depth_brace -= 1
        elif char == "(":
            depth_paren += 1
        elif char == ")":
            depth_paren -= 1
        index += 1

    return depth_brace > 0 or depth_paren > 0 or in_string


def print_execution_result(
    interpreter: Interpreter,
    result: Value | None,
    *,
    output_start: int = 0,
    out: TextIO | None = None,
) -> None:
    stream = out or sys.stdout
    for item in interpreter.output[output_start:]:
        print(item, file=stream)
    if result is not None:
        print(format_value(result), file=stream)


class InteractiveConsole:
    """Console interactive FrLang, sur le modèle de l'interpréteur Python."""

    def __init__(self, *, input_stream: TextIO | None = None, output_stream: TextIO | None = None) -> None:
        self._input = input_stream or sys.stdin
        self._output = output_stream or sys.stdout
        self._interpreter = Interpreter.session()

    @property
    def interpreter(self) -> Interpreter:
        return self._interpreter

    def run(self) -> None:
        self._print_banner()
        while True:
            try:
                source = self._read_statement()
            except EOFError:
                print(file=self._output)
                break
            except KeyboardInterrupt:
                print(file=self._output)
                continue

            stripped = source.strip()
            if not stripped:
                continue
            if stripped.lower() in _EXIT_COMMANDS:
                break
            if stripped.lower() in _HELP_COMMANDS:
                self._print_help()
                continue

            self._execute(source)

    def _read_statement(self) -> str:
        buffer = self._readline(">>> ")
        while source_needs_continuation(buffer):
            buffer += "\n" + self._readline("... ")
        return buffer

    def _readline(self, prompt: str) -> str:
        if self._input is sys.stdin and sys.stdin.isatty():
            try:
                return input(prompt)
            except EOFError:
                raise
        print(prompt, end="", file=self._output, flush=True)
        line = self._input.readline()
        if not line:
            raise EOFError
        return line.rstrip("\n")

    def _execute(self, source: str) -> None:
        output_start = len(self._interpreter.output)
        try:
            result = self._interpreter.execute(source)
        except (LexerError, ParseError) as error:
            print(error, file=sys.stderr)
            return

        print_execution_result(
            self._interpreter,
            result,
            output_start=output_start,
            out=self._output,
        )

    def _print_banner(self) -> None:
        print("FrLang — console interactive (tape « aide » ou « quitter » pour sortir)", file=self._output)

    def _print_help(self) -> None:
        print(
            "\n".join(
                [
                    "Commandes spéciales : quitter, exit, aide",
                    "Exemples :",
                    "  2 + 3",
                    '  soit nombre x = 5;',
                    "  afficher x;",
                    "  definir fonction double(nombre n) {",
                    "      retourne n * 2;",
                    "  } retourne nombre",
                    "  soit Rangee notes = nouveau Rangee(10, 20);",
                ]
            ),
            file=self._output,
        )
