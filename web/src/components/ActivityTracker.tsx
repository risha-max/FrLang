import { useEffect } from "react";
import { useLocation } from "react-router";
import { heartbeatRequest } from "../api";
import { useAuthStore } from "../stores/auth";

const HEARTBEAT_MS = 30_000;

/** Envoie un heartbeat pour compter le temps passé dans l'interface. */
export function ActivityTracker() {
  const user = useAuthStore((s) => s.user);
  const location = useLocation();

  useEffect(() => {
    if (!user?.sessionId) {
      return;
    }

    const send = () => {
      void heartbeatRequest(user.username, user.sessionId, location.pathname);
    };

    send();
    const id = window.setInterval(send, HEARTBEAT_MS);

    const onVisibility = () => {
      if (document.visibilityState === "visible") {
        send();
      }
    };
    document.addEventListener("visibilitychange", onVisibility);

    return () => {
      window.clearInterval(id);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [user?.username, user?.sessionId, location.pathname]);

  return null;
}
