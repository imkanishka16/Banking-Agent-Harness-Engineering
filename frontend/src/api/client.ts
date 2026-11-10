import type { BankState, ChatResponse, Mode, TraceEvent } from "../types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    // FastAPI sends a string for HTTPException and an array for validation errors
    const detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    throw new Error(detail ?? `${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  chat: (thread_id: string, mode: Mode, message: string) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify({ thread_id, mode, message }),
    }),

  approve: (thread_id: string, approved: boolean) =>
    request<ChatResponse>("/approve", {
      method: "POST",
      body: JSON.stringify({ thread_id, approved }),
    }),

  traces: (thread_id: string) =>
    request<TraceEvent[]>(`/traces/${encodeURIComponent(thread_id)}`),

  bank: () => request<BankState>("/bank"),

  reset: () => request<{ status: string }>("/reset", { method: "POST" }),
};