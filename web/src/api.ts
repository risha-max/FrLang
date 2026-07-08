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

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json() as Promise<T>;
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

export async function runSource(source: string): Promise<RunResponse> {
  const response = await fetch("/api/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source }),
  });
  return readJson<RunResponse>(response);
}
