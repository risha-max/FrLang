import { NavLink, Outlet, useNavigate } from "react-router";
import { clsx } from "clsx";
import { ActivityTracker } from "./ActivityTracker";
import { useAuthStore } from "../stores/auth";
import "./AppShell.css";

export function AppShell() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const isAdmin = user?.role === "admin";

  const links = isAdmin
    ? [
        { to: "/accueil", label: "Admin" },
        { to: "/progression", label: "Progression" },
        { to: "/lecons", label: "Parcours" },
        { to: "/devoir", label: "Devoirs" },
      ]
    : [
        { to: "/lecons", label: "Parcours guidé" },
        { to: "/devoir", label: "Devoirs" },
      ];

  return (
    <div className="shell">
      <a className="skip-link" href="#contenu-principal">
        Aller au contenu
      </a>
      <ActivityTracker />
      <header className="shell-header">
        <div className="shell-brand">
          <span className="shell-mark" aria-hidden="true" />
          <div>
            <p className="shell-title">FrLang</p>
            <p className="shell-subtitle">
              {isAdmin ? "Espace tuteur" : "Parcours guidé"}
            </p>
          </div>
        </div>
        <nav className="shell-nav" aria-label="Navigation principale">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                clsx("shell-link", isActive && "shell-link-active")
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="shell-user">
          {user ? (
            <>
              <span className="shell-user-name">{user.displayName}</span>
              <button
                type="button"
                className="shell-logout"
                onClick={() => {
                  void logout().then(() => {
                    navigate("/login", { replace: true });
                  });
                }}
              >
                Déconnexion
              </button>
            </>
          ) : null}
        </div>
      </header>
      <main id="contenu-principal" className="shell-main" tabIndex={-1}>
        <Outlet />
      </main>
    </div>
  );
}
