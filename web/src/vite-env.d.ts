/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_LSP_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
