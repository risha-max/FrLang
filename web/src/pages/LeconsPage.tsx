import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";
import { clsx } from "clsx";
import { fetchCurriculum, fetchProgress } from "../api";
import { isLessonUnlocked, isModuleUnlocked } from "../lib/unlock";
import { useAuthStore } from "../stores/auth";
import "./learn.css";

export default function LeconsPage() {
  const user = useAuthStore((s) => s.user)!;
  const curriculumQuery = useQuery({
    queryKey: ["curriculum"],
    queryFn: fetchCurriculum,
  });
  const progressQuery = useQuery({
    queryKey: ["progress", user.username],
    queryFn: () => fetchProgress(user.username),
    enabled: user.role !== "admin",
  });

  const lessonsState = progressQuery.data?.lessons ?? {};
  const modules = curriculumQuery.data?.modules ?? [];
  const nextLesson = progressQuery.data?.next_lesson;

  return (
    <div className="learn-page">
      <header className="learn-section-head">
        <div>
          <h1>Parcours guidé</h1>
          <p className="learn-lead">
            Termine chaque module pour débloquer le suivant.
          </p>
        </div>
        {nextLesson && user.role !== "admin" ? (
          <Link className="learn-cta" to={`/lecons/${nextLesson.id}`}>
            Continuer : {nextLesson.title}
          </Link>
        ) : null}
      </header>

      <div className="learn-modules">
        {modules.map((module, moduleIndex) => {
          const unlocked = isModuleUnlocked(modules, moduleIndex, lessonsState);
          return (
            <section
              key={module.id}
              className={clsx("learn-module", !unlocked && "is-locked")}
            >
              <div className="learn-module-head">
                <span className="learn-step">{moduleIndex + 1}</span>
                <div>
                  <h2>
                    {module.title}
                    {!unlocked ? (
                      <span className="learn-lock-tag"> Verrouillé</span>
                    ) : null}
                  </h2>
                  <p className="learn-muted">
                    {unlocked
                      ? module.summary
                      : "Termine le module précédent pour continuer."}
                  </p>
                </div>
              </div>
              <ol className="learn-lesson-list">
                {module.lessons.map((lesson) => {
                  const state = lessonsState[lesson.id];
                  const status = state?.status ?? "todo";
                  const lessonOpen =
                    user.role === "admin" ||
                    isLessonUnlocked(curriculumQuery.data, lesson.id, lessonsState);

                  if (!lessonOpen) {
                    return (
                      <li key={lesson.id}>
                        <div
                          className="learn-lesson-card is-locked"
                          aria-disabled="true"
                          aria-label={`${lesson.title} — verrouillée`}
                        >
                          <div>
                            <h3>{lesson.title}</h3>
                            <p>{lesson.summary}</p>
                          </div>
                          <span className="learn-badge">Verrouillée</span>
                        </div>
                      </li>
                    );
                  }

                  return (
                    <li key={lesson.id}>
                      <Link
                        to={`/lecons/${lesson.id}`}
                        className={clsx(
                          "learn-lesson-card",
                          status === "completed" && "is-done",
                          status === "in_progress" && "is-progress",
                        )}
                      >
                        <div>
                          <h3>{lesson.title}</h3>
                          <p>{lesson.summary}</p>
                        </div>
                        <span className="learn-badge">
                          {status === "completed"
                            ? "Terminée"
                            : status === "in_progress"
                              ? "En cours"
                              : "À faire"}
                        </span>
                      </Link>
                    </li>
                  );
                })}
              </ol>
            </section>
          );
        })}
      </div>
    </div>
  );
}
