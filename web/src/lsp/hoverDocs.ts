/** Mots du langage FrLang éligibles au survol (miroir de frlang/lsp/catalog.py). */

export const FRLANG_KEYWORDS = new Set([
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
]);

export const FRLANG_TYPES = new Set([
  "nombre",
  "logique",
  "pointeur",
  "Mots",
  "Rangee",
  "Sac",
  "Carnet",
  "Tas",
  "File",
  "Fichier",
  "Arbre",
  "Graphe",
]);

export const FRLANG_BUILTINS = new Set(["range", "adresse", "valeur", "type"]);

const KEYWORD_DOCS: Record<string, string> = {
  soit: "Déclare une variable.\n\nExemple : `soit nombre age = 12;`",
  afficher: "Affiche une valeur sur la sortie.\n\nExemple : `afficher 42;`",
  definir: "Commence la définition d'une fonction ou d'une classe.",
  fonction: "Mot-clé utilisé avec `definir` pour créer une fonction.",
  classe: "Mot-clé utilisé avec `definir` pour créer une classe.",
  herite: "Indique l'héritage d'une classe parente.",
  de: "Utilisé avec `herite de` pour nommer la classe parente.",
  constructeur: "Définit comment créer un objet de la classe.",
  retourne: "Renvoie une valeur depuis une fonction.",
  nouveau: "Crée un objet.\n\nExemple : `nouveau Rangee(1, 2, 3);`",
  si: "Exécute un bloc seulement si la condition est vraie.",
  sinon: "Bloc alternatif quand la condition du `si` est fausse.",
  tantque: "Répète un bloc tant que la condition reste vraie.",
  pourchaque:
    "Parcourt une collection.\n\nExemple : `pourchaque i dans range(5) { ... }`",
  dans: "Utilisé avec `pourchaque` : `pourchaque x dans liste`.",
  import: "Charge un autre fichier FrLang.",
  from: "Importe un symbole précis : `from module import nom;`",
  as: "Renomme un import : `import module as m;`",
  vrai: "Valeur logique vraie.",
  faux: "Valeur logique fausse.",
  rien: "Valeur vide (comme `null`).",
  mod: "Reste de la division entière.\n\nExemple : `10 mod 3` → 1",
};

const TYPE_DOCS: Record<string, string> = {
  nombre: "Nombre entier ou décimal.",
  logique: "Valeur booléenne : `vrai` ou `faux`.",
  pointeur: "Adresse mémoire vers une variable ou un élément de tableau.",
  Mots: "Texte (chaîne de caractères).",
  Rangee: "Liste ordonnée. Les indices commencent à 1.",
  Sac: "Ensemble sans doublons.",
  Carnet: "Dictionnaire : étiquette → valeur.",
  Tas: "Pile (LIFO) : dernier entré, premier sorti.",
  File: "File d'attente (FIFO) : premier entré, premier sorti.",
  Fichier: "Lecture et écriture sur le disque.",
  Arbre: "Structure parent → enfants.",
  Graphe: "Sommets reliés par des chemins.",
};

const BUILTIN_DOCS: Record<string, string> = {
  range: "Génère une `Rangee` de nombres.\n\nExemples : `range(5)`, `range(2, 10)`, `range(0, 10, 2)`",
  adresse: "Retourne l'adresse d'une variable : `adresse(x)`.",
  valeur: "Lit ou écrit via un pointeur : `valeur(p)`.",
  type: "Retourne le nom de la sorte d'une valeur.",
};

export type HoverTarget =
  | { kind: "local"; word: string; markdown: string }
  | { kind: "method"; word: string }
  | null;

export function hoverTargetForWord(
  lineText: string,
  column: number,
  word: string,
): HoverTarget {
  const index = Math.min(Math.max(column - 1, 0), lineText.length);
  const prefix = lineText.slice(0, index + 1);
  const dotMatch = prefix.match(/([A-Za-z_]\w*)\.([A-Za-z_]\w*)$/);
  if (dotMatch && dotMatch[2] === word) {
    return { kind: "method", word };
  }

  const local = localHoverMarkdown(word);
  if (local !== null) {
    return { kind: "local", word, markdown: local };
  }

  return null;
}

export function localHoverMarkdown(word: string): string | null {
  if (FRLANG_KEYWORDS.has(word)) {
    return `**${word}**\n\n${KEYWORD_DOCS[word] ?? "Mot-clé FrLang."}`;
  }
  if (FRLANG_TYPES.has(word)) {
    return `**${word}**\n\n${TYPE_DOCS[word] ?? "Sorte intégrée FrLang."}`;
  }
  if (FRLANG_BUILTINS.has(word)) {
    return `**${word}**\n\n${BUILTIN_DOCS[word] ?? "Fonction intégrée."}`;
  }
  return null;
}

export function hoverRangeForWord(
  lineNumber: number,
  wordAt: { word: string; startColumn: number; endColumn: number },
): { startLineNumber: number; startColumn: number; endLineNumber: number; endColumn: number } {
  return {
    startLineNumber: lineNumber,
    startColumn: wordAt.startColumn,
    endLineNumber: lineNumber,
    endColumn: wordAt.endColumn,
  };
}
