export type RunResponse = {
  ok: boolean;
  stdout: string[];
  result: string | null;
  error: string | null;
};

export type MainResponse = {
  source: string;
  path: string;
};

export type LoginResponse = {
  username: string;
  display_name: string;
  session_id: string;
  role: "eleve" | "admin";
};

export type LessonCheck = {
  type: string;
  value?: string;
};

export type Lesson = {
  id: string;
  title: string;
  summary: string;
  objectives: string[];
  explain: string;
  starter_code: string;
  hint?: string;
  checks: LessonCheck[];
  module_id?: string;
  module_title?: string;
};

export type Curriculum = {
  title: string;
  description: string;
  modules: Array<{
    id: string;
    title: string;
    summary: string;
    lessons: Lesson[];
  }>;
};

export type ProgressSummary = {
  username: string;
  total_lessons: number;
  completed_lessons: number;
  completion_ratio: number;
  next_lesson: { id: string; title: string; module_title?: string } | null;
  login_count: number;
  total_seconds: number;
  guided_seconds: number;
  free_seconds: number;
  runs_count: number;
  active_session: { id: string; path?: string; seconds?: number } | null;
  lessons: Record<
    string,
    {
      status: string;
      attempts: number;
      completed_at: string | null;
      last_source?: string;
      last_messages?: string[];
    }
  >;
  recent_sessions: Array<Record<string, unknown>>;
  recent_events: Array<Record<string, unknown>>;
};

export type LessonAttemptResponse = {
  passed: boolean;
  messages: string[];
  execution: RunResponse;
  progress: ProgressSummary;
  lesson: Record<string, unknown>;
};

export type DevoirSummary = {
  id: string;
  title: string;
  difficulty: string;
  points: number;
  tags: string[];
  summary: string;
  assignees: string[];
  status: string;
  attempts: number;
  completed_at: string | null;
};

export type DevoirDetail = {
  id: string;
  title: string;
  difficulty: string;
  points: number;
  tags: string[];
  summary: string;
  instructions: string;
  starter_code: string;
  sample_tests: string;
  assignees: string[];
  status: string;
  attempts: number;
  last_source: string;
};

export type DevoirRunResponse = {
  passed: boolean;
  mode: string;
  messages: string[];
  execution: RunResponse;
  devoir: Record<string, unknown>;
};

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        detail = body.detail;
      }
    } catch {
      // keep statusText
    }
    throw new Error(detail || response.statusText);
  }
  return response.json() as Promise<T>;
}

export async function loginRequest(
  username: string,
  password: string,
): Promise<LoginResponse> {
  const response = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return readJson<LoginResponse>(response);
}

export async function heartbeatRequest(
  username: string,
  sessionId: string,
  path: string,
): Promise<void> {
  await fetch("/api/session/heartbeat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, session_id: sessionId, path }),
  });
}

export async function endSessionRequest(
  username: string,
  sessionId: string,
): Promise<void> {
  await fetch("/api/session/end", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, session_id: sessionId }),
  });
}

export async function fetchCurriculum(): Promise<Curriculum> {
  const response = await fetch("/api/curriculum");
  return readJson<Curriculum>(response);
}

export async function fetchLesson(lessonId: string): Promise<Lesson> {
  const response = await fetch(`/api/curriculum/lessons/${lessonId}`);
  return readJson<Lesson>(response);
}

export async function fetchProgress(username: string): Promise<ProgressSummary> {
  const response = await fetch(`/api/progress/${encodeURIComponent(username)}`);
  return readJson<ProgressSummary>(response);
}

export async function submitLessonAttempt(
  lessonId: string,
  username: string,
  source: string,
): Promise<LessonAttemptResponse> {
  const response = await fetch(`/api/lessons/${lessonId}/attempt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, source }),
  });
  return readJson<LessonAttemptResponse>(response);
}

export async function fetchEleves(): Promise<
  Array<{ username: string; display_name: string; role: string }>
> {
  const response = await fetch("/api/eleves");
  return readJson(response);
}

export async function fetchDevoirs(
  username: string,
  role: string,
): Promise<DevoirSummary[]> {
  const params = new URLSearchParams({ username, role });
  const response = await fetch(`/api/devoirs?${params}`);
  return readJson(response);
}

export async function fetchDevoir(
  devoirId: string,
  username: string,
  role: string,
): Promise<DevoirDetail> {
  const params = new URLSearchParams({ username, role });
  const response = await fetch(`/api/devoirs/${devoirId}?${params}`);
  return readJson(response);
}

export async function runDevoir(
  devoirId: string,
  username: string,
  source: string,
  mode: "test" | "attempt",
): Promise<DevoirRunResponse> {
  const response = await fetch(`/api/devoirs/${devoirId}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, source, mode }),
  });
  return readJson(response);
}

export async function assignDevoir(
  devoirId: string,
  usernames: string[],
): Promise<DevoirDetail> {
  const response = await fetch(`/api/devoirs/${devoirId}/assign`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ usernames }),
  });
  return readJson(response);
}

export async function fetchMain(): Promise<MainResponse> {
  const response = await fetch("/api/main");
  return readJson<MainResponse>(response);
}

export async function saveMain(source: string): Promise<MainResponse> {
  const response = await fetch("/api/main", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source }),
  });
  return readJson<MainResponse>(response);
}

export async function runSource(
  source: string,
  options?: { username?: string; context?: string },
): Promise<RunResponse> {
  const response = await fetch("/api/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      source,
      username: options?.username,
      context: options?.context ?? "free",
    }),
  });
  return readJson<RunResponse>(response);
}

export function formatDuration(totalSeconds: number): string {
  const seconds = Math.max(0, Math.floor(totalSeconds));
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) {
    return `${h} h ${m} min`;
  }
  if (m > 0) {
    return `${m} min`;
  }
  return `${seconds} s`;
}
