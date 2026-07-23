import { Field } from "@base-ui/react/field";
import { Form } from "@base-ui/react/form";
import { motion, useReducedMotion } from "motion/react";
import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router";
import { Button } from "../components/ui/button";
import { useAuthStore } from "../stores/auth";
import "./LoginPage.css";

type LocationState = {
  from?: string;
};

/** Fleur de lys stylisée — palette drapeau du Québec. */
function FrLangMark(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" aria-hidden="true" {...props}>
      <rect width="48" height="48" rx="10" fill="currentColor" />
      <path
        fill="#fff"
        d="M24 8.5c.4 2.2 1.6 3.8 3.4 5.1-1.5.4-2.6 1.2-3.4 2.4-.8-1.2-1.9-2-3.4-2.4 1.8-1.3 3-2.9 3.4-5.1Zm0 9.2c1.8-1.1 3.9-1.5 6.1-1.1-.6 1.9-1.8 3.3-3.5 4.2 1.4 1.3 2.2 3 2.4 5.1-2.1-.5-3.8-1.7-4.9-3.4-1.1 1.7-2.8 2.9-4.9 3.4.2-2.1 1-3.8 2.4-5.1-1.7-.9-2.9-2.3-3.5-4.2 2.2-.4 4.3 0 6.1 1.1Zm0 11.8c.9-1.4 2.3-2.4 4.1-2.9-.2 2.2-1.2 4-2.8 5.4.8.7 1.4 1.7 1.7 2.9-1.5-.3-2.7-1-3-2.1-.3 1.1-1.5 1.8-3 2.1.3-1.2.9-2.2 1.7-2.9-1.6-1.4-2.6-3.2-2.8-5.4 1.8.5 3.2 1.5 4.1 2.9Z"
      />
    </svg>
  );
}

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const reduceMotion = useReducedMotion();
  const user = useAuthStore((s) => s.user);
  const login = useAuthStore((s) => s.login);
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const fromState =
    (location.state as LocationState | null)?.from &&
    (location.state as LocationState).from !== "/login"
      ? (location.state as LocationState).from!
      : null;

  if (user) {
    return (
      <Navigate
        to={fromState ?? (user.role === "admin" ? "/accueil" : "/lecons")}
        replace
      />
    );
  }

  const goAfterLogin = () => {
    const logged = useAuthStore.getState().user;
    const dest =
      fromState ?? (logged?.role === "admin" ? "/accueil" : "/lecons");
    navigate(dest, { replace: true });
  };

  return (
    <div className="login-page">
      <motion.div
        className="login-shell"
        initial={reduceMotion ? false : { opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={
          reduceMotion
            ? { duration: 0 }
            : { duration: 0.35, ease: [0.22, 1, 0.36, 1] }
        }
      >
        <header className="login-brand">
          <FrLangMark className="login-logo" />
          <h1 className="login-brand-name">FrLang</h1>
          <p className="login-brand-tag">
            Apprends les bases du code en français, pas à pas.
          </p>
        </header>

        <section className="login-panel" aria-labelledby="login-heading">
          <h2 id="login-heading" className="login-title">
            Connexion
          </h2>

          <Form
            className="login-form"
            onFormSubmit={(values) => {
              void (async () => {
                setFormError(null);
                const username = String(values.username ?? "").trim();
                const password = String(values.password ?? "");
                if (!username || !password) {
                  setFormError("Entre ton nom d’utilisateur et ton mot de passe.");
                  return;
                }
                setSubmitting(true);
                try {
                  await login(username, password);
                  goAfterLogin();
                } catch (err) {
                  setFormError(
                    err instanceof Error
                      ? err.message
                      : "Identifiant ou mot de passe incorrect.",
                  );
                } finally {
                  setSubmitting(false);
                }
              })();
            }}
          >
            <Field.Root name="username" className="login-field">
              <Field.Label className="login-label">Nom d’utilisateur</Field.Label>
              <Field.Control
                type="text"
                required
                autoComplete="username"
                placeholder="prenom"
                className="login-control"
              />
              <Field.Error className="login-error" />
            </Field.Root>

            <Field.Root name="password" className="login-field">
              <Field.Label className="login-label">Mot de passe</Field.Label>
              <div className="login-control-wrap">
                <Field.Control
                  type={showPassword ? "text" : "password"}
                  required
                  autoComplete="current-password"
                  placeholder="••••••••"
                  className="login-control has-toggle"
                />
                <button
                  type="button"
                  className="login-toggle"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-pressed={showPassword}
                  aria-label={
                    showPassword
                      ? "Masquer le mot de passe"
                      : "Afficher le mot de passe"
                  }
                >
                  {showPassword ? "Masquer" : "Afficher"}
                </button>
              </div>
              <Field.Error className="login-error" />
            </Field.Root>

            {formError ? (
              <p className="login-error" role="alert">
                {formError}
              </p>
            ) : null}

            <Button type="submit" intent="primary" size="lg" disabled={submitting}>
              {submitting ? "Connexion…" : "Se connecter"}
            </Button>
          </Form>

          <p className="login-note">
            Ton compte est créé par ton tuteur — pas d’inscription en ligne.
          </p>

          <div className="login-mocks" aria-label="Comptes mock pour tests UI">
            <p className="login-mocks-title">Comptes mock (UI/UX)</p>
            <ul className="login-mocks-list">
              {[
                {
                  username: "admin",
                  password: "admin",
                  label: "Admin · métriques",
                },
                {
                  username: "nouveau",
                  password: "nouveau",
                  label: "Débutant · 0%",
                },
                {
                  username: "encours",
                  password: "encours",
                  label: "En cours · ~33%",
                },
                {
                  username: "avance",
                  password: "avance",
                  label: "Avancé · ~89%",
                },
              ].map((account) => (
                <li key={account.username}>
                  <button
                    type="button"
                    className="login-mock-btn"
                    disabled={submitting}
                    onClick={() => {
                      void (async () => {
                        setFormError(null);
                        setSubmitting(true);
                        try {
                          await login(account.username, account.password);
                          goAfterLogin();
                        } catch (err) {
                          setFormError(
                            err instanceof Error
                              ? err.message
                              : "Identifiant ou mot de passe incorrect.",
                          );
                        } finally {
                          setSubmitting(false);
                        }
                      })();
                    }}
                  >
                    <strong>
                      {account.username} / {account.password}
                    </strong>
                    <span>{account.label}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <p className="login-footer">
          Accès aux leçons FrLang pour les élèves inscrits.
        </p>
      </motion.div>
    </div>
  );
}
