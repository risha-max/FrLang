#!/usr/bin/env python3
"""Évalue des expressions et de petits programmes FrLang."""

from __future__ import annotations

import sys

from frlang import Interpreter, LexerError, ParseError
from frlang.lexer import Lexer
from frlang.types import Value, format_value


def evaluate(source: str) -> tuple[Value | None, list[str]]:
    interpreter = Interpreter(source)
    value = interpreter.run()
    return value, interpreter.output


def print_tokens(source: str) -> None:
    for token in Lexer(source).tokenize():
        if token.kind.name == "EOF":
            print("EOF")
            continue
        print(f"{token.kind.name:12} {token.value!r:>12}  (ligne {token.line}, col {token.column})")


def repl() -> None:
    print("FrLang — tape « quitter » pour sortir")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue
        if line.lower() in {"quitter", "exit", "quit"}:
            break

        try:
            value, output = evaluate(line)
            for item in output:
                print(item)
            if value is not None:
                print(format_value(value))
        except (LexerError, ParseError) as error:
            print(error)


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--tokens":
        source = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else sys.stdin.read()
        print_tokens(source.strip())
        return 0

    if len(sys.argv) > 1:
        try:
            value, output = evaluate(" ".join(sys.argv[1:]))
            for item in output:
                print(item)
            if value is not None:
                print(format_value(value))
        except (LexerError, ParseError) as error:
            print(error, file=sys.stderr)
            return 1
        return 0

    repl()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
