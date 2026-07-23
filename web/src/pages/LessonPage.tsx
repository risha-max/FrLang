import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Editor, { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import { useCallback, useEffect, useRef, useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router";
import {
  fetchCurriculum,
  fetchLesson,
  fetchProgress,
  submitLessonAttempt,
} from "../api";
import { LessonRichText } from "../components/LessonRichText";
import { isLessonUnlocked } from "../lib/unlock";
import { FrLangLspClient } from "../lsp/client";
import { registerFrLangProviders } from "../lsp/providers";
import {
  FRLANG_DOCUMENT_URI,
  FRLANG_LANGUAGE_ID,
  registerFrLangLanguage,
} from "../monaco/frlang";
import { useAuthStore } from "../stores/auth";
import "./learn.css";

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

export default function LessonPage() {
  const { lessonId = "" } = useParams();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user)!;
  const queryClient = useQueryClient();
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const lspRef = useRef<FrLangLspClient | null>(null);
  const advanceTimeoutRef = useRef<number | null>(null);
  const [source, setSource] = useState("");
  const [showHint, setShowHint] = useState(false);
  const [advancingTo, setAdvancingTo] = useState<string | null>(null);
  const [lspStatus, setLspStatus] = useState<"connecting" | "ready" | "error">(
    "connecting",
  );

  const curriculumQuery = useQuery({
    queryKey: ["curriculum"],
    queryFn: fetchCurriculum,
  });

  const lessonQuery = useQuery({
    queryKey: ["lesson", lessonId],
    queryFn: () => fetchLesson(lessonId),
    enabled: Boolean(lessonId),
  });

  const progressQuery = useQuery({
    queryKey: ["progress", user.username],
    queryFn: () => fetchProgress(user.username),
    enabled: user.role !== "admin",
  });

  const unlocked =
    user.role === "admin" ||
    isLessonUnlocked(
      curriculumQuery.data,
      lessonId,
      progressQuery.data?.lessons,
    );

  useEffect(() => {
    setAdvancingTo(null);
    if (advanceTimeoutRef.current !== null) {
      window.clearTimeout(advanceTimeoutRef.current);
      advanceTimeoutRef.current = null;
    }
  }, [lessonId]);

  useEffect(() => {
    const lesson = lessonQuery.data;
    if (!lesson) {
      return;
    }
    const saved = progressQuery.data?.lessons?.[lesson.id]?.last_source;
    setSource(saved || lesson.starter_code || "");
    setShowHint(false);
  }, [lessonQuery.data, progressQuery.data]);

  useEffect(() => {
    if (lspStatus === "ready" && source) {
      lspRef.current?.notifyChange(source);
    }
  }, [lspStatus, source]);

  const debouncedLsp = useDebouncedCallback((nextSource: string) => {
    lspRef.current?.notifyChange(nextSource);
  }, 250);

  const attemptMutation = useMutation({
    mutationFn: () => {
      const current = editorRef.current?.getValue() ?? source;
      setSource(current);
      return submitLessonAttempt(lessonId, user.username, current);
    },
    onSuccess: (data) => {
      void queryClient.invalidateQueries({ queryKey: ["progress", user.username] });
      if (!data.passed || user.role === "admin") {
        return;
      }
      const nextId = data.progress.next_lesson?.id ?? null;
      const nextTitle = data.progress.next_lesson?.title ?? null;
      if (advanceTimeoutRef.current !== null) {
        window.clearTimeout(advanceTimeoutRef.current);
      }
      if (nextId) {
        setAdvancingTo(nextTitle ?? nextId);
        advanceTimeoutRef.current = window.setTimeout(() => {
          navigate(`/lecons/${nextId}`, { replace: true });
        }, 1200);
      } else {
        setAdvancingTo("parcours terminé");
        advanceTimeoutRef.current = window.setTimeout(() => {
          navigate("/lecons", { replace: true });
        }, 1200);
      }
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
      if (advanceTimeoutRef.current !== null) {
        window.clearTimeout(advanceTimeoutRef.current);
      }
    };
  }, []);

  const lesson = lessonQuery.data;
  const result = attemptMutation.data;
  const status = progressQuery.data?.lessons?.[lessonId]?.status;

  if (
    user.role !== "admin" &&
    curriculumQuery.isSuccess &&
    progressQuery.isSuccess &&
    !unlocked
  ) {
    return <Navigate to="/lecons" replace />;
  }

  if (lessonQuery.isError) {
    return (
      <div className="learn-page">
        <p className="learn-error">Leçon introuvable.</p>
        <Link to="/lecons">Retour aux leçons</Link>
      </div>
    );
  }

  return (
    <div className="learn-page lesson-layout">
      <aside className="lesson-brief">
        <Link className="learn-back" to="/lecons">
          ← Leçons
        </Link>
        <p className="learn-kicker">{lesson?.module_title}</p>
        <h1>{lesson?.title ?? "…"}</h1>
        {lesson?.explain ? (
          <LessonRichText
            as="p"
            className="learn-lead lesson-explain"
            text={lesson.explain}
          />
        ) : (
          <p className="learn-lead">…</p>
        )}
        <h2>Objectifs</h2>
        <ul className="lesson-objectives">
          {(lesson?.objectives ?? []).map((item) => (
            <LessonRichText key={item} as="li" text={item} />
          ))}
        </ul>
        {lesson?.hint ? (
          <div className="lesson-hint-box">
            <button
              type="button"
              className="learn-btn learn-btn-ghost"
              onClick={() => setShowHint((v) => !v)}
            >
              {showHint ? "Masquer l’indice" : "Voir un indice"}
            </button>
            {showHint ? (
              <p className="lesson-hint">
                <LessonRichText text={lesson.hint} />
              </p>
            ) : null}
          </div>
        ) : null}
        {status === "completed" ? (
          <p className="lesson-done-flag">Leçon complétée</p>
        ) : null}
        {advancingTo ? (
          <p className="lesson-advance-flag">
            {advancingTo === "parcours terminé"
              ? "Parcours terminé — retour à la liste…"
              : `Bravo — prochaine leçon : ${advancingTo}…`}
          </p>
        ) : null}
      </aside>

      <section className="lesson-work">
        <div className="lesson-toolbar">
          <span className={`status status-${lspStatus}`}>
            LSP : {lspStatus}
          </span>
          <button
            type="button"
            className="learn-cta"
            disabled={attemptMutation.isPending || !lesson}
            onClick={() => attemptMutation.mutate()}
          >
            {attemptMutation.isPending ? "Vérification…" : "Exécuter et vérifier"}
          </button>
          <button
            type="button"
            className="learn-btn learn-btn-secondary"
            onClick={() => setSource(lesson?.starter_code ?? "")}
          >
            Réinitialiser
          </button>
        </div>
        <div className="lesson-editor">
          <Editor
            height="100%"
            path={FRLANG_DOCUMENT_URI}
            language={FRLANG_LANGUAGE_ID}
            theme="frlang-dark"
            value={source}
            onChange={(value) => {
              const next = value ?? "";
              setSource(next);
              debouncedLsp(next);
            }}
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
        </div>
        <div className="lesson-feedback">
          {result ? (
            <>
              <p className={result.passed ? "learn-success" : "learn-error"}>
                {result.passed ? "Objectifs atteints" : "Pas encore…"}
              </p>
              <ul>
                {result.messages.map((message) => (
                  <li key={message}>{message}</li>
                ))}
              </ul>
              <pre className="lesson-output">
                {result.execution.error
                  ? result.execution.error
                  : result.execution.stdout.join("\n") || "(aucune sortie)"}
              </pre>
            </>
          ) : (
            <p className="learn-muted">
              Écris ton code, puis clique sur « Exécuter et vérifier ».
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
