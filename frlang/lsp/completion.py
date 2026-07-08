from __future__ import annotations

import re
from dataclasses import dataclass

from frlang.lsp.catalog import (
    BUILTINS,
    KEYWORDS,
    METHOD_SNIPPETS,
    OBJECT_METHODS,
    TYPES,
)
from frlang.lsp.symbols import extract_symbols

_DOT_PATTERN = re.compile(r"([A-Za-z_]\w*)\.(\w*)$")
_PREFIX_PATTERN = re.compile(r"([A-Za-z_]\w*)$")


@dataclass(frozen=True, slots=True)
class CompletionSuggestion:
    label: str
    kind: str
    detail: str | None = None
    insert_text: str | None = None


def suggest_completions(source: str, line: int, character: int) -> list[CompletionSuggestion]:
    lines = source.splitlines()
    if line < 0 or line >= len(lines):
        line_text = ""
    else:
        line_text = lines[line][:character]

    prefix = _word_prefix(line_text)
    variables, functions, classes = extract_symbols(source)

    dot_match = _DOT_PATTERN.search(line_text)
    if dot_match:
        receiver, method_prefix = dot_match.group(1), dot_match.group(2)
        return _method_completions(receiver, method_prefix, variables, classes)

    if _ends_with_keyword(line_text, "soit"):
        return _filter(_type_suggestions(), prefix)

    if _ends_with_keyword(line_text, "import") or _ends_with_keyword(line_text, "from"):
        return _filter(_keyword_suggestions(("as",)), prefix)

    suggestions = (
        _keyword_suggestions(KEYWORDS)
        + _literal_suggestions()
        + _builtin_suggestions()
        + _type_suggestions()
        + _variable_suggestions(variables)
        + _function_suggestions(functions)
        + _class_suggestions(classes)
    )
    return _filter(suggestions, prefix)


def _method_completions(
    receiver: str,
    method_prefix: str,
    variables: dict[str, str],
    classes: set[str],
) -> list[CompletionSuggestion]:
    receiver_type = variables.get(receiver)
    if receiver_type is None:
        if receiver in classes:
            receiver_type = receiver
        else:
            return []

    methods = list(OBJECT_METHODS.get(receiver_type, ()))
    if receiver_type in classes:
        methods.extend(("afficher", "equals"))

    suggestions = [
        CompletionSuggestion(
            label=method,
            kind="method",
            detail=f"{receiver_type}.{method}()",
            insert_text=METHOD_SNIPPETS.get(method, f"{method}()"),
        )
        for method in methods
    ]
    return _filter(suggestions, method_prefix)


def _keyword_suggestions(words: tuple[str, ...] | list[str]) -> list[CompletionSuggestion]:
    return [CompletionSuggestion(label=word, kind="keyword") for word in words]


def _literal_suggestions() -> list[CompletionSuggestion]:
    return [
        CompletionSuggestion(label="vrai", kind="keyword", detail="logique"),
        CompletionSuggestion(label="faux", kind="keyword", detail="logique"),
        CompletionSuggestion(label="rien", kind="keyword", detail="valeur vide"),
    ]


def _builtin_suggestions() -> list[CompletionSuggestion]:
    return [
        CompletionSuggestion(
            label=name,
            kind="function",
            detail="builtin",
            insert_text=METHOD_SNIPPETS.get(name, f"{name}()"),
        )
        for name in BUILTINS
    ]


def _type_suggestions() -> list[CompletionSuggestion]:
    return [CompletionSuggestion(label=name, kind="type", detail="sorte") for name in TYPES]


def _variable_suggestions(variables: dict[str, str]) -> list[CompletionSuggestion]:
    return [
        CompletionSuggestion(label=name, kind="variable", detail=var_type)
        for name, var_type in sorted(variables.items())
    ]


def _function_suggestions(functions: set[str]) -> list[CompletionSuggestion]:
    return [
        CompletionSuggestion(
            label=name,
            kind="function",
            insert_text=f"{name}()",
        )
        for name in sorted(functions)
    ]


def _class_suggestions(classes: set[str]) -> list[CompletionSuggestion]:
    return [
        CompletionSuggestion(
            label=name,
            kind="class",
            detail="classe",
            insert_text=f"nouveau {name}()",
        )
        for name in sorted(classes)
    ]


def _word_prefix(line_text: str) -> str:
    match = _PREFIX_PATTERN.search(line_text)
    return match.group(1) if match else ""


def _ends_with_keyword(line_text: str, keyword: str) -> bool:
    stripped = line_text.rstrip()
    return stripped == keyword or stripped.endswith(f" {keyword}")


def _filter(
    suggestions: list[CompletionSuggestion],
    prefix: str,
) -> list[CompletionSuggestion]:
    if not prefix:
        return _dedupe(suggestions)
    lowered = prefix.lower()
    filtered = [
        item
        for item in suggestions
        if item.label.lower().startswith(lowered)
    ]
    return _dedupe(filtered)


def _dedupe(suggestions: list[CompletionSuggestion]) -> list[CompletionSuggestion]:
    seen: set[str] = set()
    unique: list[CompletionSuggestion] = []
    for item in suggestions:
        if item.label in seen:
            continue
        seen.add(item.label)
        unique.append(item)
    return unique
