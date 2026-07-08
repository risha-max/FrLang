import type * as Monaco from "monaco-editor";
import {
  FRLANG_BUILTINS,
  FRLANG_KEYWORDS,
  FRLANG_TYPES,
} from "./hoverDocs";

export type LocalCompletion = {
  label: string;
  kind: Monaco.languages.CompletionItemKind;
  insertText: string;
  detail?: string;
  sortText?: string;
};

const SNIPPETS: Record<string, string> = {
  range: "range($0)",
  adresse: "adresse($0)",
  valeur: "valeur($0)",
  type: "type($0)",
  definir: "definir fonction ${1:nom}($0) {\n\t$2\n}",
  pourchaque: "pourchaque ${1:i} dans ${2:collection} {\n\t$0\n}",
  si: "si ${1:condition} {\n\t$0\n}",
  tantque: "tantque ${1:condition} {\n\t$0\n}",
};

export function localCompletions(
  monaco: typeof Monaco,
  prefix: string,
): LocalCompletion[] {
  const lowered = prefix.toLowerCase();
  const items: LocalCompletion[] = [];

  const push = (
    label: string,
    kind: Monaco.languages.CompletionItemKind,
    detail: string,
    sortGroup: string,
  ) => {
    if (lowered && !label.toLowerCase().startsWith(lowered)) {
      return;
    }
    items.push({
      label,
      kind,
      insertText: SNIPPETS[label] ?? label,
      detail,
      sortText: `${sortGroup}_${label}`,
    });
  };

  for (const keyword of FRLANG_KEYWORDS) {
    push(keyword, monaco.languages.CompletionItemKind.Keyword, "mot-clé", "0");
  }
  for (const typeName of FRLANG_TYPES) {
    push(typeName, monaco.languages.CompletionItemKind.Class, "sorte", "1");
  }
  for (const builtin of FRLANG_BUILTINS) {
    push(
      builtin,
      monaco.languages.CompletionItemKind.Function,
      "builtin",
      "2",
    );
  }

  return items;
}

export function isMethodContext(linePrefix: string): boolean {
  return /[A-Za-z_]\w*\.\w*$/.test(linePrefix);
}
