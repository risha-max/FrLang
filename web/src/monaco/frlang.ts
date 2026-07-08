import type * as Monaco from "monaco-editor";

const KEYWORDS = [
  "soit",
  "afficher",
  "definir",
  "fonction",
  "classe",
  "herite",
  "de",
  "constructeur",
  "retourne",
  "nouveau",
  "si",
  "sinon",
  "tantque",
  "pourchaque",
  "dans",
  "import",
  "from",
  "as",
  "vrai",
  "faux",
  "rien",
  "mod",
];

export const FRLANG_LANGUAGE_ID = "frlang";
export const FRLANG_DOCUMENT_URI = "file:///main.frlang";

export function registerFrLangLanguage(monaco: typeof Monaco): void {
  if (monaco.languages.getLanguages().some((lang) => lang.id === FRLANG_LANGUAGE_ID)) {
    return;
  }

  monaco.languages.register({ id: FRLANG_LANGUAGE_ID });
  monaco.languages.setLanguageConfiguration(FRLANG_LANGUAGE_ID, {
    wordPattern: /(-?\d*\.\d\w*)|([A-Za-z_]\w*)/,
    comments: {
      lineComment: "//",
    },
    brackets: [
      ["{", "}"],
      ["(", ")"],
      ["[", "]"],
    ],
    autoClosingPairs: [
      { open: "{", close: "}" },
      { open: "(", close: ")" },
      { open: '"', close: '"' },
    ],
  });
  monaco.languages.setMonarchTokensProvider(FRLANG_LANGUAGE_ID, {
    keywords: KEYWORDS,
    tokenizer: {
      root: [
        [/\/\/.*$/, "comment"],
        [/"([^"\\]|\\.)*$/, "string.invalid"],
        [/"/, "string", "@string"],
        [/\b\d+(\.\d+)?\b/, "number"],
        [
          /\b(soit|afficher|definir|fonction|classe|herite|de|constructeur|retourne|nouveau|si|sinon|tantque|pourchaque|dans|import|from|as|vrai|faux|rien|mod)\b/,
          "keyword",
        ],
        [
          /\b(nombre|logique|pointeur|Mots|Rangee|Sac|Carnet|Tas|File|Fichier|Arbre|Graphe)\b/,
          "type",
        ],
        [/\b(range|adresse|valeur|type)\b/, "builtin"],
        [/[{}()[\];,.:]/, "delimiter"],
        [/[=<>!+\-*/^%]+/, "operator"],
        [/[A-Za-z_]\w*/, "identifier"],
        [/\s+/, "white"],
      ],
      string: [
        [/[^\\"]+/, "string"],
        [/\\./, "string.escape"],
        [/"/, "string", "@pop"],
      ],
    },
  });

  monaco.editor.defineTheme("frlang-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "keyword", foreground: "C586C0", fontStyle: "bold" },
      { token: "type", foreground: "4EC9B0" },
      { token: "builtin", foreground: "DCDCAA" },
      { token: "string", foreground: "CE9178" },
      { token: "number", foreground: "B5CEA8" },
      { token: "comment", foreground: "6A9955" },
    ],
    colors: {
      "editor.background": "#1e1e1e",
    },
  });
}
