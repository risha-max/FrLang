from frlang.lsp.completion import suggest_completions
from frlang.lsp.diagnostics import analyze_source


def test_completion_keywords() -> None:
    suggestions = suggest_completions("so", 0, 2)
    labels = {item.label for item in suggestions}
    assert "soit" in labels


def test_completion_after_soit_offers_types() -> None:
    suggestions = suggest_completions("soit ", 0, 5)
    labels = {item.label for item in suggestions}
    assert "nombre" in labels
    assert "Mots" in labels


def test_completion_mots_methods() -> None:
    source = "soit Mots mot = nouveau Mots(\"abc\");\nmot."
    suggestions = suggest_completions(source, 1, 4)
    labels = {item.label for item in suggestions}
    assert "inverser" in labels
    assert "taille" in labels


def test_completion_local_function() -> None:
    source = "definir fonction saluer() { } retourne nombre\nsal"
    suggestions = suggest_completions(source, 1, 3)
    labels = {item.label for item in suggestions}
    assert "saluer" in labels


def test_diagnostics_reports_syntax_error() -> None:
    messages = analyze_source("soit nombre x = ;")
    assert len(messages) == 1
    assert "x" in messages[0].message
