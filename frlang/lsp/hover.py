from __future__ import annotations

import re

from frlang.lsp.docs import lookup_documentation
from frlang.lsp.symbols import extract_symbols

_DOT_PATTERN = re.compile(r"([A-Za-z_]\w*)\.(\w*)$")
_IDENTIFIER_PATTERN = re.compile(r"[A-Za-z_]\w*")


def hover_at_position(source: str, line: int, character: int) -> str | None:
    lines = source.splitlines()
    if line < 0 or line >= len(lines):
        return None

    line_text = lines[line]
    prefix = _prefix_through_cursor(line_text, character)
    variables, _, classes = extract_symbols(source)

    dot_match = _DOT_PATTERN.search(prefix)
    if dot_match:
        receiver, method = dot_match.group(1), dot_match.group(2)
        receiver_type = variables.get(receiver)
        if receiver_type is None and receiver in classes:
            receiver_type = receiver
        if receiver_type is not None and method:
            doc = lookup_documentation(method, receiver_type)
            if doc is not None:
                return doc

    word = _identifier_at(line_text, character)
    if word is None:
        return None

    return lookup_documentation(word)


def _prefix_through_cursor(line_text: str, character: int) -> str:
    index = min(max(character, 0), len(line_text))
    if index < len(line_text) and _is_identifier_char(line_text[index]):
        end = index + 1
        while end < len(line_text) and _is_identifier_char(line_text[end]):
            end += 1
        return line_text[:end]
    return line_text[:index]


def _identifier_at(line_text: str, character: int) -> str | None:
    index = min(max(character, 0), len(line_text))
    for match in _IDENTIFIER_PATTERN.finditer(line_text):
        if match.start() < index <= match.end():
            return match.group(0)
        if index == match.start() and match.group(0):
            return match.group(0)
    if index > 0:
        for match in _IDENTIFIER_PATTERN.finditer(line_text):
            if match.end() == index:
                return match.group(0)
    return None


def _is_identifier_char(char: str) -> bool:
    return char.isalnum() or char == "_"
