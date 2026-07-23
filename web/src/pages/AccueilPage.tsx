import { Link } from "react-router";
import "./learn.css";

/** Accueil admin uniquement — les élèves vont au parcours guidé. */
export default function AccueilPage() {
  return (
    <div className="learn-page">
      <header className="learn-section-head">
        <div>
          <p className="learn-kicker">Espace tuteur</p>
          <h1>Administration</h1>
          <p className="learn-lead">
            Les métriques sont réservées à l’admin. Les élèves suivent le
            parcours guidé (module verrouillé tant que le précédent n’est pas
            terminé).
          </p>
        </div>
      </header>

      <section className="learn-grid learn-grid-2">
        <article className="learn-panel">
          <h2>En un coup d’œil</h2>
          <p className="learn-muted">
            Connexions, temps, leçons et exécutions par élève.
          </p>
          <Link className="learn-cta" to="/progression">
            Voir la progression
          </Link>
        </article>
        <article className="learn-panel">
          <h2>Devoirs</h2>
          <p className="learn-muted">
            Assigne des problèmes aux élèves (UI type kata).
          </p>
          <Link className="learn-btn learn-btn-secondary" to="/devoir">
            Gérer les devoirs
          </Link>
        </article>
      </section>
    </div>
  );
}
