import { Navigate, Route, Routes } from "react-router";
import { useEffect, useState } from "react";
import { RequireAdmin, RequireAuth } from "./components/auth/RequireAuth";
import { AppShell } from "./components/AppShell";
import AccueilPage from "./pages/AccueilPage";
import DevoirListPage from "./pages/DevoirListPage";
import DevoirWorkspacePage from "./pages/DevoirWorkspacePage";
import LeconsPage from "./pages/LeconsPage";
import LessonPage from "./pages/LessonPage";
import LoginPage from "./pages/LoginPage";
import ProgressionPage from "./pages/ProgressionPage";
import { useAuthStore } from "./stores/auth";

function HomeRedirect() {
  const user = useAuthStore((s) => s.user);
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <Navigate to={user.role === "admin" ? "/accueil" : "/lecons"} replace />;
}

function useAuthHydrated() {
  const [hydrated, setHydrated] = useState(() =>
    useAuthStore.persist.hasHydrated(),
  );

  useEffect(() => {
    if (hydrated) {
      return;
    }
    return useAuthStore.persist.onFinishHydration(() => setHydrated(true));
  }, [hydrated]);

  return hydrated;
}

export default function App() {
  const hydrated = useAuthHydrated();

  if (!hydrated) {
    return null;
  }

  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route
          path="/accueil"
          element={
            <RequireAdmin>
              <AccueilPage />
            </RequireAdmin>
          }
        />
        <Route path="/lecons" element={<LeconsPage />} />
        <Route path="/lecons/:lessonId" element={<LessonPage />} />
        <Route path="/devoir" element={<DevoirListPage />} />
        <Route path="/devoir/:devoirId" element={<DevoirWorkspacePage />} />
        <Route
          path="/progression"
          element={
            <RequireAdmin>
              <ProgressionPage />
            </RequireAdmin>
          }
        />
      </Route>
      <Route path="/atelier" element={<Navigate to="/lecons" replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
