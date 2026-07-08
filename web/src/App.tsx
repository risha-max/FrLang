import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Editor, { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import { useCallback, useEffect, useRef, useState } from "react";
import { fetchMain, runSource, saveMain } from "./api";
import { FrLangLspClient } from "./lsp/client";
import { registerFrLangProviders } from "./lsp/providers";
import {
  FRLANG_DOCUMENT_URI,
  FRLANG_LANGUAGE_ID,
  registerFrLangLanguage,
} from "./monaco/frlang";
import "./App.css";

loader.config({ monaco });
registerFrLangLanguage(monaco);
registerFrLangProviders(monaco);

const LSP_URL =
  import.meta.env.VITE_LSP_URL ??
  `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/lsp`;

function useDebouncedCallback<T extends (...args: never[]) => void>(
  callback: T,
  delayMs: number,
): T {
  const timeoutRef = useRef<number | null>(null);
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  return useCallback(
    ((...args: Parameters<T>) => {
      if (timeoutRef.current !== null) {
        window.clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = window.setTimeout(() => {
        callbackRef.current(...args);
      }, delayMs);
    }) as T,
    [delayMs],
  );
}

export default function App() {
  const queryClient = useQueryClient();
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const lspRef = useRef<FrLangLspClient | null>(null);
  const runGenerationRef = useRef(0);
  const [source, setSource] = useState("");
  const [stdout, setStdout] = useState<string[]>([]);
  const [runError, setRunError] = useState<string | null>(null);
  const [runResult, setRunResult] = useState<string | null>(null);
  const [lspStatus, setLspStatus] = useState<"connecting" | "ready" | "error">(
    "connecting",
  );

  const mainQuery = useQuery({
    queryKey: ["main"],
    queryFn: fetchMain,
  });

  useEffect(() => {
    if (mainQuery.data?.source !== undefined && source === "") {
      setSource(mainQuery.data.source);
    }
  }, [mainQuery.data?.source, source]);

  useEffect(() => {
    if (lspStatus === "ready" && source) {
      lspRef.current?.notifyChange(source);
    }
  }, [lspStatus, source]);

  const saveMutation = useMutation({
    mutationFn: saveMain,
    onSuccess: (data) => {
      queryClient.setQueryData(["main"], data);
    },
  });

  const debouncedSave = useDebouncedCallback((nextSource: string) => {
    saveMutation.mutate(nextSource);
  }, 600);

  const debouncedLsp = useDebouncedCallback((nextSource: string) => {
    lspRef.current?.notifyChange(nextSource);
  }, 250);

  const runMutation = useMutation({
    mutationFn: runSource,
    onMutate: () => {
      runGenerationRef.current += 1;
      return { generation: runGenerationRef.current };
    },
    onSuccess: (data, _variables, context) => {
      if (context?.generation !== runGenerationRef.current) {
        return;
      }
      setStdout(data.stdout);
      setRunResult(data.result);
      setRunError(data.ok ? null : data.error);
    },
  });

  const handleMount = useCallback(
    async (editor: monaco.editor.IStandaloneCodeEditor) => {
      editorRef.current = editor;
      const uri = monaco.Uri.parse(FRLANG_DOCUMENT_URI);
      let model = monaco.editor.getModel(uri) ?? editor.getModel();
      if (!model || model.uri.toString() !== uri.toString()) {
        const text = model?.getValue() ?? editor.getValue() ?? "";
        model = monaco.editor.createModel(text, FRLANG_LANGUAGE_ID, uri);
        editor.setModel(model);
      }

      const client = new FrLangLspClient();
      lspRef.current = client;
      try {
        await client.connect(monaco, model, LSP_URL, setLspStatus);
        client.notifyChange(model.getValue());
      } catch {
        setLspStatus("error");
      }
    },
    [],
  );

  useEffect(() => {
    return () => {
      lspRef.current?.dispose();
    };
  }, []);

  const handleRun = () => {
    const current = editorRef.current?.getValue() ?? source;
    setSource(current);
    saveMutation.mutate(current);
    runMutation.mutate(current);
  };

  const handleChange = (value: string | undefined) => {
    const next = value ?? "";
    setSource(next);
    debouncedSave(next);
    debouncedLsp(next);
  };

  return (
    <div className="app">
      <header className="toolbar">
        <div>
          <h1>FrLang</h1>
          <p className="subtitle">main.frlang — atelier web</p>
        </div>
        <div className="toolbar-actions">
          <span className={`status status-${lspStatus}`}>
            LSP : {lspStatus}
          </span>
          <button
            type="button"
            className="primary"
            onClick={handleRun}
            disabled={runMutation.isPending}
          >
            {runMutation.isPending ? "Exécution…" : "Exécuter"}
          </button>
        </div>
      </header>

      <main className="workspace">
        <section className="editor-panel">
          <Editor
            height="100%"
            path={FRLANG_DOCUMENT_URI}
            language={FRLANG_LANGUAGE_ID}
            theme="frlang-dark"
            value={source}
            onChange={handleChange}
            onMount={handleMount}
            options={{
              fontSize: 15,
              minimap: { enabled: false },
              automaticLayout: true,
              scrollBeyondLastLine: false,
              wordWrap: "on",
              hover: { enabled: true, delay: 300 },
              quickSuggestions: {
                other: true,
                comments: false,
                strings: false,
              },
              suggestOnTriggerCharacters: true,
              wordBasedSuggestions: "off",
              tabCompletion: "on",
            }}
          />
        </section>

        <section className="output-panel">
          <h2>Sortie</h2>
          {runError ? <pre className="output error">{runError}</pre> : null}
          <pre className="output">
            {stdout.length === 0 && !runResult && !runError
              ? "Clique sur Exécuter pour lancer le programme."
              : stdout.join("\n")}
            {runResult ? `\n${runResult}` : ""}
          </pre>
          <p className="hint">
            {saveMutation.isPending
              ? "Enregistrement…"
              : saveMutation.isSuccess
                ? "main.frlang enregistré"
                : "Sauvegarde automatique"}
          </p>
        </section>
      </main>
    </div>
  );
}
