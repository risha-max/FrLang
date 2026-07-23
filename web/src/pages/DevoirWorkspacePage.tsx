import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Editor, { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import { clsx } from "clsx";
import { fetchDevoir, runDevoir } from "../api";
import { LessonRichText } from "../components/LessonRichText";
import {
  FRLANG_LANGUAGE_ID,
  registerFrLangLanguage,
} from "../monaco/frlang";
import { useAuthStore } from "../stores/auth";
import "./devoir.css";

loader.config({ monaco });
registerFrLangLanguage(monaco);

type SideTab = "instructions" | "output";

export default function DevoirWorkspacePage() {
  const { devoirId = "" } = useParams();
  const user = useAuthStore((s) => s.user)!;
  const queryClient = useQueryClient();
  const [source, setSource] = useState("");
  const [sideTab, setSideTab] = useState<SideTab>("instructions");

  const devoirQuery = useQuery({
    queryKey: ["devoir", devoirId, user.username],
    queryFn: () => fetchDevoir(devoirId, user.username, user.role),
    enabled: Boolean(devoirId),
  });

  useEffect(() => {
    const devoir = devoirQuery.data;
    if (!devoir) {
      return;
    }
    setSource(devoir.last_source || devoir.starter_code || "");
  }, [devoirQuery.data]);

  const runMutation = useMutation({
    mutationFn: (mode: "test" | "attempt") =>
      runDevoir(devoirId, user.username, source, mode),
    onSuccess: (data) => {
      setSideTab("output");
      if (data.mode === "attempt") {
        void queryClient.invalidateQueries({ queryKey: ["devoirs"] });
        void queryClient.invalidateQueries({
          queryKey: ["devoir", devoirId, user.username],
        });
      }
    },
  });

  const devoir = devoirQuery.data;
  const result = runMutation.data;

  if (devoirQuery.isError) {
    return (
      <div className="kata-error-page">
        <p>Devoir introuvable ou non assigné.</p>
        <Link to="/devoir">Retour aux devoirs</Link>
      </div>
    );
  }

  return (
    <div className="kata">
      <header className="kata-top">
        <div className="kata-top-left">
          <Link to="/devoir" className="kata-back">
            ← Devoirs
          </Link>
          <span className={clsx("devoir-diff", `diff-${devoir?.difficulty}`)}>
            {devoir?.difficulty ?? "…"}
          </span>
          <h1>{devoir?.title ?? "Chargement…"}</h1>
        </div>
        <div className="kata-top-meta">
          <span>{devoir?.points ?? 0} pts</span>
          <span>
            {devoir?.status === "completed"
              ? "Réussi"
              : `${devoir?.attempts ?? 0} tentative(s)`}
          </span>
          <span className="kata-lang">FrLang</span>
        </div>
      </header>

      <div className="kata-body">
        <aside className="kata-side">
          <div className="kata-tabs" role="tablist" aria-label="Panneau latéral">
            <button
              type="button"
              id="tab-instructions"
              role="tab"
              aria-controls="panel-instructions"
              aria-selected={sideTab === "instructions"}
              tabIndex={sideTab === "instructions" ? 0 : -1}
              className={clsx(sideTab === "instructions" && "is-active")}
              onClick={() => setSideTab("instructions")}
            >
              Instructions
            </button>
            <button
              type="button"
              id="tab-output"
              role="tab"
              aria-controls="panel-output"
              aria-selected={sideTab === "output"}
              tabIndex={sideTab === "output" ? 0 : -1}
              className={clsx(sideTab === "output" && "is-active")}
              onClick={() => setSideTab("output")}
            >
              Output
            </button>
          </div>

          <div
            id="panel-instructions"
            role="tabpanel"
            aria-labelledby="tab-instructions"
            hidden={sideTab !== "instructions"}
            className="kata-side-content"
          >
            {devoir?.instructions ? (
              <LessonRichText
                as="p"
                className="kata-instructions"
                text={devoir.instructions}
              />
            ) : (
              <p className="kata-instructions">…</p>
            )}
            <div className="kata-tags">
              {(devoir?.tags ?? []).map((tag) => (
                <span key={tag}>{tag}</span>
              ))}
            </div>
          </div>

          <div
            id="panel-output"
            role="tabpanel"
            aria-labelledby="tab-output"
            hidden={sideTab !== "output"}
            className="kata-side-content"
          >
            <div className="kata-output" aria-live="polite">
              {result ? (
                <>
                  <p className={result.passed ? "kata-pass" : "kata-fail"}>
                    {result.mode === "attempt"
                      ? result.passed
                        ? "Soumission réussie"
                        : "Soumission échouée"
                      : result.passed
                        ? "Tests OK"
                        : "Tests incomplets"}
                  </p>
                  <ul>
                    {result.messages.map((message) => (
                      <li key={message}>{message}</li>
                    ))}
                  </ul>
                  <pre>
                    {result.execution.error
                      ? result.execution.error
                      : result.execution.stdout.join("\n") ||
                        "(aucune sortie)"}
                  </pre>
                </>
              ) : (
                <p className="kata-muted">
                  Lance <strong>Tester</strong> ou <strong>Soumettre</strong>{" "}
                  pour voir la sortie ici.
                </p>
              )}
            </div>
          </div>
        </aside>

        <section className="kata-editors" aria-label="Éditeurs de code">
          <div className="kata-panel">
            <div className="kata-panel-head">
              <span id="label-solution">Solution</span>
            </div>
            <div
              className="kata-editor"
              role="group"
              aria-labelledby="label-solution"
            >
              <Editor
                height="100%"
                language={FRLANG_LANGUAGE_ID}
                theme="frlang-dark"
                value={source}
                onChange={(value) => setSource(value ?? "")}
                options={{
                  fontSize: 14,
                  minimap: { enabled: false },
                  automaticLayout: true,
                  scrollBeyondLastLine: false,
                  wordWrap: "on",
                  ariaLabel: "Éditeur de solution FrLang",
                }}
              />
            </div>
          </div>

          <div className="kata-panel kata-panel-tests">
            <div className="kata-panel-head">
              <span id="label-sample-tests">Exemples / Sample Tests</span>
            </div>
            <div
              className="kata-editor"
              role="group"
              aria-labelledby="label-sample-tests"
            >
              <Editor
                height="100%"
                language={FRLANG_LANGUAGE_ID}
                theme="frlang-dark"
                value={devoir?.sample_tests ?? ""}
                options={{
                  readOnly: true,
                  fontSize: 13,
                  minimap: { enabled: false },
                  automaticLayout: true,
                  scrollBeyondLastLine: false,
                  wordWrap: "on",
                  lineNumbers: "off",
                  ariaLabel: "Tests d’exemple en lecture seule",
                }}
              />
            </div>
          </div>
        </section>
      </div>

      <footer className="kata-actions">
        <div className="kata-actions-left">
          <button
            type="button"
            className="kata-btn ghost"
            onClick={() => setSource(devoir?.starter_code ?? "")}
          >
            Reset
          </button>
        </div>
        <div className="kata-actions-right">
          <button
            type="button"
            className="kata-btn"
            disabled={runMutation.isPending || !devoir}
            onClick={() => runMutation.mutate("test")}
          >
            {runMutation.isPending && runMutation.variables === "test"
              ? "Test…"
              : "Tester"}
          </button>
          <button
            type="button"
            className="kata-btn primary"
            disabled={runMutation.isPending || !devoir}
            onClick={() => runMutation.mutate("attempt")}
          >
            {runMutation.isPending && runMutation.variables === "attempt"
              ? "Soumission…"
              : "Soumettre"}
          </button>
        </div>
      </footer>
    </div>
  );
}
