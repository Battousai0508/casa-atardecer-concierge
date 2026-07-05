const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
const APP_NAME = process.env.NEXT_PUBLIC_AGENT_APP_NAME ?? "app";

export interface AdkPart {
  text?: string;
  thought?: boolean;
  functionCall?: { name?: string };
  functionResponse?: { name?: string };
}

export interface AdkEvent {
  author?: string;
  partial?: boolean;
  content?: {
    role?: string;
    parts?: AdkPart[];
  };
  errorMessage?: string;
}

export async function createSession(userId: string): Promise<string> {
  const res = await fetch(
    `${API_URL}/apps/${APP_NAME}/users/${encodeURIComponent(userId)}/sessions`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    }
  );
  if (!res.ok) {
    throw new Error(`No se pudo crear la sesión (HTTP ${res.status})`);
  }
  const data = await res.json();
  return data.id as string;
}

export async function* streamAgentRun(params: {
  userId: string;
  sessionId: string;
  text: string;
  signal?: AbortSignal;
}): AsyncGenerator<AdkEvent> {
  const res = await fetch(`${API_URL}/run_sse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    signal: params.signal,
    body: JSON.stringify({
      app_name: APP_NAME,
      user_id: params.userId,
      session_id: params.sessionId,
      new_message: {
        role: "user",
        parts: [{ text: params.text }],
      },
      streaming: true,
    }),
  });

  if (!res.ok || !res.body) {
    const detail = await res.text().catch(() => "");
    throw new Error(`Error del agente (HTTP ${res.status}) ${detail}`.trim());
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let separator;
    while ((separator = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, separator);
      buffer = buffer.slice(separator + 2);

      for (const line of rawEvent.split("\n")) {
        if (!line.startsWith("data:")) continue;
        const payload = line.slice(5).trim();
        if (!payload) continue;
        try {
          yield JSON.parse(payload) as AdkEvent;
        } catch {
          // Ignore malformed SSE chunks
        }
      }
    }
  }
}
