"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { createSession, streamAgentRun } from "@/lib/agent-client";

type Role = "user" | "assistant" | "error";

interface Message {
  id: string;
  role: Role;
  text: string;
  streaming?: boolean;
}

const SUGGESTIONS = [
  "¿Dónde está ubicada la casa?",
  "¿Hay disponibilidad este fin de semana?",
  "¿Qué servicios incluye la estancia?",
];

function getUserId(): string {
  const key = "casa-atardecer-user-id";
  let id = localStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(key, id);
  }
  return id;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [toolStatus, setToolStatus] = useState<string | null>(null);

  const sessionRef = useRef<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, toolStatus]);

  useEffect(() => () => abortRef.current?.abort(), []);

  const updateMessage = (id: string, patch: Partial<Message>) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === id ? { ...m, ...patch } : m))
    );
  };

  const send = useCallback(
    async (rawText: string) => {
      const text = rawText.trim();
      if (!text || busy) return;

      setBusy(true);
      setInput("");
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "user", text },
      ]);

      const assistantId = crypto.randomUUID();
      setMessages((prev) => [
        ...prev,
        { id: assistantId, role: "assistant", text: "", streaming: true },
      ]);

      const abort = new AbortController();
      abortRef.current = abort;

      try {
        const userId = getUserId();
        if (!sessionRef.current) {
          sessionRef.current = await createSession(userId);
        }

        const segments: string[] = [];
        let partial = "";

        for await (const event of streamAgentRun({
          userId,
          sessionId: sessionRef.current,
          text,
          signal: abort.signal,
        })) {
          if (event.errorMessage) {
            throw new Error(event.errorMessage);
          }
          // Internal routing output ({"category": ...}) — never shown to the guest
          if (event.author === "classifier_agent") continue;
          for (const part of event.content?.parts ?? []) {
            if (part.thought) continue;
            if (part.functionCall) setToolStatus("Consultando información…");
            if (part.functionResponse) setToolStatus(null);
            if (part.text) {
              if (event.partial) {
                partial += part.text;
              } else {
                segments.push(part.text);
                partial = "";
              }
            }
          }
          const combined = [...segments, partial].filter(Boolean).join("\n\n");
          if (combined) updateMessage(assistantId, { text: combined });
        }

        const finalText = [...segments, partial].filter(Boolean).join("\n\n");
        updateMessage(assistantId, {
          text:
            finalText ||
            "Lo siento, no pude generar una respuesta. Intenta de nuevo.",
          streaming: false,
        });
      } catch (err) {
        updateMessage(assistantId, {
          role: "error",
          streaming: false,
          text:
            err instanceof Error && err.name !== "AbortError"
              ? `No pude conectar con el concierge. ${err.message}`
              : "Conversación interrumpida.",
        });
      } finally {
        setToolStatus(null);
        setBusy(false);
        abortRef.current = null;
      }
    },
    [busy]
  );

  const reset = () => {
    abortRef.current?.abort();
    sessionRef.current = null;
    setMessages([]);
    setToolStatus(null);
    setBusy(false);
  };

  const empty = messages.length === 0;

  return (
    <div className="flex h-[36rem] w-full flex-col overflow-hidden rounded-3xl border border-neutral-200 bg-white shadow-[0_24px_60px_-24px_rgba(17,17,17,0.25)]">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-neutral-100 px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="relative flex h-2.5 w-2.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-60" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-accent" />
          </span>
          <div>
            <p className="text-sm font-medium tracking-wide text-neutral-900">
              Concierge Casa Atardecer
            </p>
            <p className="text-xs text-neutral-400">Siempre disponible</p>
          </div>
        </div>
        <button
          onClick={reset}
          className="rounded-full border border-neutral-200 px-4 py-1.5 text-xs tracking-wide text-neutral-500 transition hover:border-accent hover:text-accent"
        >
          Nueva conversación
        </button>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-6 py-5">
        {empty && (
          <div className="flex h-full flex-col items-center justify-center gap-6 text-center">
            <div>
              <p className="font-display text-3xl text-neutral-900">
                Bienvenido a Casa Atardecer
              </p>
              <p className="mt-2 max-w-sm text-sm leading-relaxed text-neutral-400">
                Soy tu concierge personal. Pregúntame sobre la casa, la
                disponibilidad o cualquier detalle de tu estancia.
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-full border border-neutral-200 bg-white px-4 py-2 text-xs text-neutral-600 transition hover:border-accent hover:text-accent"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={
                m.role === "user"
                  ? "max-w-[80%] rounded-3xl rounded-br-md bg-neutral-900 px-5 py-3 text-sm leading-relaxed text-white"
                  : m.role === "error"
                    ? "max-w-[80%] rounded-3xl rounded-bl-md border border-red-100 bg-red-50 px-5 py-3 text-sm leading-relaxed text-red-600"
                    : "max-w-[80%] rounded-3xl rounded-bl-md bg-neutral-100 px-5 py-3 text-sm leading-relaxed text-neutral-800"
              }
            >
              {m.role === "assistant" && m.text ? (
                <div className="prose prose-sm max-w-none prose-neutral prose-p:my-1.5 prose-p:leading-relaxed prose-headings:my-2 prose-headings:font-medium prose-strong:text-neutral-900 prose-ul:my-1.5 prose-ol:my-1.5 prose-li:my-0.5 prose-a:text-accent prose-a:no-underline hover:prose-a:underline">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {m.text}
                  </ReactMarkdown>
                </div>
              ) : (
                m.text
              ) ||
                (m.streaming && (
                  <span className="inline-flex gap-1 py-1">
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-accent [animation-delay:-0.3s]" />
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-accent [animation-delay:-0.15s]" />
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-accent" />
                  </span>
                ))}
            </div>
          </div>
        ))}

        {toolStatus && (
          <p className="pl-2 text-xs italic text-neutral-400">{toolStatus}</p>
        )}
      </div>

      {/* Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="border-t border-neutral-100 p-4"
      >
        <div className="flex items-center gap-2 rounded-full border border-neutral-200 bg-neutral-50 py-1.5 pl-5 pr-1.5 transition focus-within:border-accent">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe tu mensaje…"
            disabled={busy}
            className="flex-1 bg-transparent text-sm text-neutral-900 outline-none placeholder:text-neutral-400 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={busy || !input.trim()}
            aria-label="Enviar"
            className="flex h-9 w-9 items-center justify-center rounded-full bg-accent text-white transition hover:bg-accent-dark disabled:opacity-40"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M5 12h14" />
              <path d="M13 6l6 6-6 6" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}
