import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";
import { useState } from "react";
import {
  fetchEleves,
  fetchProgress,
  formatDuration,
  type ProgressSummary,
} from "../api";
import { useAuthStore } from "../stores/auth";
import "./learn.css";

function eventLabel(kind: unknown): string {
  switch (kind) {
    case "login":
      return "Connexion";
    case "logout":
      return "Déconnexion";
    case "run":
      return "Exécution";
    case "lesson_attempt":
      return "Tentative de leçon";
    case "lesson_completed":
      return "Leçon complétée";
    default:
      return String(kind ?? "Événement");
  }
}

function Metrics({ progress }: { progress: ProgressSummary | undefined }) {
  return (
    <>
      <section className="learn-grid">
        <article className="learn-panel">
          <h2>En un coup d’œil</h2>
          <ul className="learn-stats">
            <li>
              <strong>
                {progress?.completed_lessons ?? 0}/{progress?.total_lessons ?? 0}
              </strong>
              <span>leçons</span>
            </li>
            <li>
              <strong>{progress?.login_count ?? 0}</strong>
              <span>connexions</span>
            </li>
            <li>
              <strong>{formatDuration(progress?.total_seconds ?? 0)}</strong>
              <span>temps total</span>
            </li>
            <li>
              <strong>{progress?.runs_count ?? 0}</strong>
              <span>exécutions</span>
            </li>
          </ul>
        </article>

        <article className="learn-panel">
          <h2>Temps</h2>
          <ul className="learn-stats">
            <li>
              <strong>{formatDuration(progress?.guided_seconds ?? 0)}</strong>
              <span>parcours guidé</span>
            </li>
            <li>
              <strong>{formatDuration(progress?.free_seconds ?? 0)}</strong>
              <span>hors leçons</span>
            </li>
            <li>
              <strong>{Math.round((progress?.completion_ratio ?? 0) * 100)}%</strong>
              <span>complété</span>
            </li>
          </ul>
        </article>
      </section>

      <section className="learn-panel learn-panel-wide">
        <h2>Activité récente</h2>
        <ul className="learn-timeline">
          {(progress?.recent_events ?? []).map((event, index) => (
            <li key={`${String(event.at)}-${index}`}>
              <span className="learn-timeline-kind">{eventLabel(event.kind)}</span>
              <span className="learn-muted">
                {event.at ? new Date(String(event.at)).toLocaleString("fr-CA") : ""}
                {event.lesson_id ? ` · ${String(event.lesson_id)}` : ""}
              </span>
            </li>
          ))}
          {(progress?.recent_events ?? []).length === 0 ? (
            <li className="learn-muted">Aucune activité encore.</li>
          ) : null}
        </ul>
      </section>
    </>
  );
}

export default function ProgressionPage() {
  const user = useAuthStore((s) => s.user)!;
  const elevesQuery = useQuery({
    queryKey: ["eleves"],
    queryFn: fetchEleves,
    enabled: user.role === "admin",
  });
  const [selected, setSelected] = useState<string>("");

  const targetUsername =
    user.role === "admin"
      ? selected || elevesQuery.data?.[0]?.username || ""
      : user.username;

  const progressQuery = useQuery({
    queryKey: ["progress", targetUsername],
    queryFn: () => fetchProgress(targetUsername),
    enabled: Boolean(targetUsername) && user.role === "admin",
  });

  if (user.role !== "admin") {
    return null;
  }

  return (
    <div className="learn-page">
      <header className="learn-section-head">
        <div>
          <h1>Progression (admin)</h1>
          <p className="learn-lead">
            Métriques réservées au tuteur pour évaluer l’apprentissage.
          </p>
        </div>
        <Link className="learn-btn learn-btn-secondary" to="/lecons">
          Parcours guidé
        </Link>
      </header>

      <label className="learn-select-label">
        Élève
        <select
          className="learn-select"
          value={targetUsername}
          onChange={(event) => setSelected(event.target.value)}
        >
          {(elevesQuery.data ?? []).map((eleve) => (
            <option key={eleve.username} value={eleve.username}>
              {eleve.display_name} ({eleve.username})
            </option>
          ))}
        </select>
      </label>

      <Metrics progress={progressQuery.data} />
    </div>
  );
}
