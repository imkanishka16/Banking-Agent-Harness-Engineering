import { useCallback, useEffect, useState } from "react";

import { api } from "../api/client";
import type { ApprovalRequest, BankState, ChatMessage, ChatResponse, Mode, TraceEvent } from "../types";

interface ModeState {
  threadId: string;
  messages: ChatMessage[];
  events: TraceEvent[];
  pendingApproval: ApprovalRequest | null;
}

const newId = () => crypto.randomUUID();
const emptyState = (): ModeState => ({
  threadId: newId().slice(0, 8),
  messages: [],
  events: [],
  pendingApproval: null,
});

export function useChat() {
  const [mode, setMode] = useState<Mode>("harnessed");
  const [states, setStates] = useState<Record<Mode, ModeState>>({
    naive: emptyState(),
    harnessed: emptyState(),
  });
  const [bank, setBank] = useState<BankState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const current = states[mode];

  const refreshBank = useCallback(async () => {
    try {
      setBank(await api.bank());
    } catch {
      /* the bank panel just shows stale data; the chat still works */
    }
  }, []);

  useEffect(() => {
    refreshBank();
  }, [refreshBank]);

  const update = (m: Mode, fn: (s: ModeState) => ModeState) =>
    setStates((prev) => ({ ...prev, [m]: fn(prev[m]) }));

  const addMessage = (m: Mode, role: ChatMessage["role"], content: string) =>
    update(m, (s) => ({ ...s, messages: [...s.messages, { id: newId(), role, content }] }));

  const applyResponse = (m: Mode, res: ChatResponse) =>
    update(m, (s) => ({
      ...s,
      events: [...s.events, ...res.events],
      pendingApproval: res.approval,
      messages: res.reply
        ? [...s.messages, { id: newId(), role: "agent", content: res.reply }]
        : s.messages,
    }));

  const run = async (m: Mode, call: () => Promise<ChatResponse>) => {
    setLoading(true);
    setError(null);
    try {
      applyResponse(m, await call());
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
      refreshBank(); // always show the real state of the money afterwards
    }
  };

  const send = async (text: string) => {
    const message = text.trim();
    if (!message || loading || current.pendingApproval) return;
    const m = mode;
    addMessage(m, "user", message);
    await run(m, () => api.chat(states[m].threadId, m, message));
  };

  const decide = async (approved: boolean) => {
    const m = mode;
    if (!states[m].pendingApproval) return;
    update(m, (s) => ({ ...s, pendingApproval: null }));
    addMessage(m, "system", approved ? "You approved the transfer." : "You declined the transfer.");
    await run(m, () => api.approve(states[m].threadId, approved));
  };

  const reset = async () => {
    try {
      await api.reset();
    } finally {
      setStates({ naive: emptyState(), harnessed: emptyState() });
      setError(null);
      refreshBank();
    }
  };

  return {
    mode,
    setMode,
    messages: current.messages,
    events: current.events,
    pendingApproval: current.pendingApproval,
    bank,
    loading,
    error,
    send,
    decide,
    reset,
  };
}