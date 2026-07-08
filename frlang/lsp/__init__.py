"""Serveur Language Server Protocol pour FrLang."""

from frlang.lsp.completion import CompletionSuggestion, suggest_completions
from frlang.lsp.diagnostics import analyze_source

__all__ = [
    "CompletionSuggestion",
    "analyze_source",
    "suggest_completions",
]
