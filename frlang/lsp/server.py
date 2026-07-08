"""Serveur LSP FrLang.

Transports supportés (via pygls) :
- stdio (défaut) : VS Code, Cursor, Neovim
- --ws : navigateur (Monaco + WebSocket)
- --tcp : client LSP distant

Exemples :
    frlang-lsp
    frlang-lsp --ws --host 127.0.0.1 --port 8765
"""

from __future__ import annotations

import sys

from frlang.lsp.completion import CompletionSuggestion, suggest_completions
from frlang.lsp.diagnostics import DiagnosticMessage, analyze_source


def _require_pygls():
    try:
        from lsprotocol import types
        from pygls.cli import start_server
        from pygls.lsp.server import LanguageServer
    except ImportError as error:
        raise SystemExit(
            "Le serveur LSP nécessite pygls.\n"
            "Installe-le avec : pip install -e '.[lsp]'"
        ) from error
    return types, start_server, LanguageServer


def _kind_for(suggestion: CompletionSuggestion, types):
    mapping = {
        "keyword": types.CompletionItemKind.Keyword,
        "type": types.CompletionItemKind.Class,
        "method": types.CompletionItemKind.Method,
        "function": types.CompletionItemKind.Function,
        "variable": types.CompletionItemKind.Variable,
        "class": types.CompletionItemKind.Class,
    }
    return mapping.get(suggestion.kind, types.CompletionItemKind.Text)


def _to_completion_items(suggestions: list[CompletionSuggestion], types):
    items = []
    for suggestion in suggestions:
        item = types.CompletionItem(
            label=suggestion.label,
            kind=_kind_for(suggestion, types),
            detail=suggestion.detail,
        )
        if suggestion.insert_text is not None:
            item.insert_text = suggestion.insert_text
        items.append(item)
    return items


def _to_lsp_diagnostics(messages: list[DiagnosticMessage], types):
    diagnostics = []
    for message in messages:
        text = message.message
        if message.hint:
            text = f"{text}\n\nAstuce : {message.hint}"
        diagnostics.append(
            types.Diagnostic(
                range=types.Range(
                    start=types.Position(line=max(message.line - 1, 0), character=max(message.column - 1, 0)),
                    end=types.Position(line=max(message.line - 1, 0), character=max(message.column, 0)),
                ),
                message=text,
                severity=types.DiagnosticSeverity.Error,
                source="frlang",
            )
        )
    return diagnostics


def build_server():
    types, _, LanguageServer = _require_pygls()

    server = LanguageServer(
        "frlang-lsp",
        "0.1.0",
        text_document_sync_kind=types.TextDocumentSyncKind.Full,
    )

    def publish_document_diagnostics(uri: str, source: str) -> None:
        diagnostics = _to_lsp_diagnostics(analyze_source(source), types)
        server.text_document_publish_diagnostics(
            types.PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics)
        )

    @server.feature(
        types.TEXT_DOCUMENT_COMPLETION,
        types.CompletionOptions(trigger_characters=[".", " "]),
    )
    def completions(params: types.CompletionParams):
        document = server.workspace.get_text_document(params.text_document.uri)
        suggestions = suggest_completions(
            document.source,
            params.position.line,
            params.position.character,
        )
        return types.CompletionList(
            is_incomplete=False,
            items=_to_completion_items(suggestions, types),
        )

    @server.feature(types.TEXT_DOCUMENT_DID_OPEN)
    def did_open(params: types.DidOpenTextDocumentParams):
        publish_document_diagnostics(params.text_document.uri, params.text_document.text)

    @server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
    def did_change(params: types.DidChangeTextDocumentParams):
        document = server.workspace.get_text_document(params.text_document.uri)
        publish_document_diagnostics(params.text_document.uri, document.source)

    @server.feature(types.TEXT_DOCUMENT_DID_SAVE)
    def did_save(params: types.DidSaveTextDocumentParams):
        document = server.workspace.get_text_document(params.text_document.uri)
        publish_document_diagnostics(params.text_document.uri, document.source)

    return server


def main(argv: list[str] | None = None) -> int:
    try:
        _, start_server, _ = _require_pygls()
        start_server(build_server(), list(argv if argv is not None else sys.argv[1:]))
        return 0
    except SystemExit as error:
        print(str(error), file=sys.stderr)
        return 1
