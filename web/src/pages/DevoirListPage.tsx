import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router";
import { clsx } from "clsx";
import { assignDevoir, fetchDevoirs, fetchEleves } from "../api";
import { useAuthStore } from "../stores/auth";
import "./devoir.css";

export default function DevoirListPage() {
  const user = useAuthStore((s) => s.user)!;
  const queryClient = useQueryClient();
  const isAdmin = user.role === "admin";

  const devoirsQuery = useQuery({
    queryKey: ["devoirs", user.username, user.role],
    queryFn: () => fetchDevoirs(user.username, user.role),
  });

  const elevesQuery = useQuery({
    queryKey: ["eleves"],
    queryFn: fetchEleves,
    enabled: isAdmin,
  });

  const assignMutation = useMutation({
    mutationFn: ({
      devoirId,
      usernames,
    }: {
      devoirId: string;
      usernames: string[];
    }) => assignDevoir(devoirId, usernames),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["devoirs"] });
    },
  });

  return (
    <div className="devoir-list-page">
      <header className="devoir-list-head">
        <div>
          <p className="devoir-kicker">Problèmes assignés</p>
          <h1>Devoirs</h1>
          <p className="devoir-lead">
            {isAdmin
              ? "Assigne des problèmes aux élèves. Ils les résolvent dans l’espace devoir."
              : "Résous les problèmes que ton tuteur t’a assignés."}
          </p>
        </div>
      </header>

      <ul className="devoir-cards">
        {(devoirsQuery.data ?? []).map((devoir) => (
          <li key={devoir.id} className="devoir-card">
            <div className="devoir-card-top">
              <span className={clsx("devoir-diff", `diff-${devoir.difficulty}`)}>
                {devoir.difficulty}
              </span>
              <span className="devoir-points">{devoir.points} pts</span>
            </div>
            <h2>
              <Link to={`/devoir/${devoir.id}`}>{devoir.title}</Link>
            </h2>
            <p>{devoir.summary}</p>
            <div className="devoir-tags">
              {devoir.tags.map((tag) => (
                <span key={tag}>{tag}</span>
              ))}
            </div>
            <div className="devoir-card-foot">
              <span
                className={clsx(
                  "devoir-status",
                  devoir.status === "completed" && "is-done",
                )}
              >
                {devoir.status === "completed"
                  ? "Réussi"
                  : devoir.status === "in_progress"
                    ? "En cours"
                    : "À faire"}
              </span>
              <Link className="devoir-open" to={`/devoir/${devoir.id}`}>
                Ouvrir
              </Link>
            </div>
            {isAdmin ? (
              <div className="devoir-assign">
                <p className="devoir-assign-label">Assigné à</p>
                <div className="devoir-assign-grid">
                  {(elevesQuery.data ?? []).map((eleve) => {
                    const checked = devoir.assignees.includes(eleve.username);
                    return (
                      <label key={eleve.username}>
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => {
                            const next = checked
                              ? devoir.assignees.filter((u) => u !== eleve.username)
                              : [...devoir.assignees, eleve.username];
                            assignMutation.mutate({
                              devoirId: devoir.id,
                              usernames: next,
                            });
                          }}
                        />
                        {eleve.display_name}
                      </label>
                    );
                  })}
                </div>
              </div>
            ) : null}
          </li>
        ))}
      </ul>

      {(devoirsQuery.data ?? []).length === 0 ? (
        <p className="devoir-empty">Aucun devoir pour le moment.</p>
      ) : null}
    </div>
  );
}
