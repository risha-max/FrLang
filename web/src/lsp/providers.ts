import type * as Monaco from "monaco-editor";
import {
  CompletionItem,
  CompletionItemKind,
  Hover,
} from "vscode-languageserver-protocol";
import { FRLANG_LANGUAGE_ID } from "../monaco/frlang";
import { isMethodContext, localCompletions } from "./completions";
import {
  hoverRangeForWord,
  hoverTargetForWord,
} from "./hoverDocs";

const LSP_TIMEOUT_MS = 2_000;

export type LspBridge = {
  requestHover(
    line: number,
    character: number,
  ): Promise<Hover | null>;
  requestCompletion(
    line: number,
    character: number,
  ): Promise<CompletionItem[] | { items?: CompletionItem[] } | null>;
  isReady(): boolean;
};

let lspBridge: LspBridge | null = null;

export function setLspBridge(bridge: LspBridge | null): void {
  lspBridge = bridge;
}

function withTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const timer = window.setTimeout(() => reject(new Error("lsp timeout")), timeoutMs);
    promise
      .then((value) => {
        window.clearTimeout(timer);
        resolve(value);
      })
      .catch((error: unknown) => {
        window.clearTimeout(timer);
        reject(error);
      });
  });
}

function hoverMarkdown(hover: Hover): string | null {
  if (!hover.contents) {
    return null;
  }
  if (typeof hover.contents === "string") {
    return hover.contents;
  }
  if (Array.isArray(hover.contents)) {
    return hover.contents
      .map((entry) => (typeof entry === "string" ? entry : entry.value))
      .join("\n\n");
  }
  return hover.contents.value;
}

function toMonacoKind(
  monaco: typeof Monaco,
  kind: CompletionItemKind | undefined,
): Monaco.languages.CompletionItemKind {
  switch (kind) {
    case CompletionItemKind.Keyword:
      return monaco.languages.CompletionItemKind.Keyword;
    case CompletionItemKind.Method:
      return monaco.languages.CompletionItemKind.Method;
    case CompletionItemKind.Function:
      return monaco.languages.CompletionItemKind.Function;
    case CompletionItemKind.Variable:
      return monaco.languages.CompletionItemKind.Variable;
    case CompletionItemKind.Class:
      return monaco.languages.CompletionItemKind.Class;
    default:
      return monaco.languages.CompletionItemKind.Text;
  }
}

export function registerFrLangProviders(monaco: typeof Monaco): Monaco.IDisposable[] {
  const disposables: Monaco.IDisposable[] = [];

  disposables.push(
    monaco.languages.registerHoverProvider(FRLANG_LANGUAGE_ID, {
      provideHover: async (textModel, position, token) => {
        if (token.isCancellationRequested) {
          return null;
        }

        const wordAt = textModel.getWordAtPosition(position);
        if (!wordAt?.word) {
          return null;
        }

        const lineText = textModel.getLineContent(position.lineNumber);
        const target = hoverTargetForWord(lineText, position.column, wordAt.word);
        if (target === null) {
          return null;
        }

        const hoverRange = hoverRangeForWord(position.lineNumber, wordAt);
        const range = new monaco.Range(
          hoverRange.startLineNumber,
          hoverRange.startColumn,
          hoverRange.endLineNumber,
          hoverRange.endColumn,
        );

        if (target.kind === "local") {
          return {
            range,
            contents: [{ value: target.markdown, isTrusted: true }],
          };
        }

        const bridge = lspBridge;
        if (!bridge?.isReady() || token.isCancellationRequested) {
          return null;
        }

        try {
          const hover = await withTimeout(
            bridge.requestHover(position.lineNumber - 1, position.column - 1),
            LSP_TIMEOUT_MS,
          );
          if (token.isCancellationRequested || !hover?.contents) {
            return null;
          }
          const value = hoverMarkdown(hover);
          if (!value) {
            return null;
          }
          return {
            range,
            contents: [{ value, isTrusted: true }],
          };
        } catch {
          return null;
        }
      },
    }),
  );

  disposables.push(
    monaco.languages.registerCompletionItemProvider(FRLANG_LANGUAGE_ID, {
      triggerCharacters: [".", " "],
      provideCompletionItems: async (textModel, position, _context, token) => {
        if (token.isCancellationRequested) {
          return { suggestions: [] };
        }

        const word = textModel.getWordUntilPosition(position);
        const prefix = word.word;
        const linePrefix = textModel.getValueInRange({
          startLineNumber: position.lineNumber,
          startColumn: 1,
          endLineNumber: position.lineNumber,
          endColumn: position.column,
        });
        const range = {
          startLineNumber: position.lineNumber,
          startColumn: word.startColumn,
          endLineNumber: position.lineNumber,
          endColumn: word.endColumn,
        };

        const local = localCompletions(monaco, prefix).map((item) => ({
          label: item.label,
          kind: item.kind,
          insertText: item.insertText,
          detail: item.detail,
          sortText: item.sortText,
          range,
          insertTextRules: item.insertText.includes("$")
            ? monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
            : undefined,
        }));

        const bridge = lspBridge;
        const needsLsp =
          bridge?.isReady() === true &&
          (isMethodContext(linePrefix) || prefix.length > 0);

        if (!needsLsp || !bridge) {
          return { suggestions: local };
        }

        try {
          const result = await withTimeout(
            bridge.requestCompletion(position.lineNumber - 1, position.column - 1),
            LSP_TIMEOUT_MS,
          );
          if (token.isCancellationRequested || !result) {
            return { suggestions: local };
          }
          const items = Array.isArray(result) ? result : (result.items ?? []);
          const lspSuggestions = items.map((item) => ({
            label: item.label,
            kind: toMonacoKind(monaco, item.kind),
            insertText: item.insertText ?? item.label,
            detail: item.detail,
            range,
            insertTextRules:
              item.insertText?.includes("$") === true
                ? monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
                : undefined,
          }));

          const seen = new Set<string>();
          const merged = [...lspSuggestions, ...local].filter((item) => {
            if (seen.has(item.label)) {
              return false;
            }
            seen.add(item.label);
            return true;
          });
          return { suggestions: merged };
        } catch {
          return { suggestions: local };
        }
      },
    }),
  );

  return disposables;
}
