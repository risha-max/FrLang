import { create } from "zustand";
import { persist } from "zustand/middleware";
import { endSessionRequest, loginRequest } from "../api";

export type UserRole = "eleve" | "admin";

export type AuthUser = {
  username: string;
  displayName: string;
  sessionId: string;
  role: UserRole;
};

type AuthState = {
  user: AuthUser | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      login: async (username, password) => {
        const data = await loginRequest(username, password);
        set({
          user: {
            username: data.username,
            displayName: data.display_name,
            sessionId: data.session_id,
            role: data.role === "admin" ? "admin" : "eleve",
          },
        });
      },
      logout: async () => {
        const current = get().user;
        if (current?.sessionId) {
          try {
            await endSessionRequest(current.username, current.sessionId);
          } catch {
            // ignore network errors on logout
          }
        }
        set({ user: null });
      },
    }),
    { name: "frlang-auth" },
  ),
);
