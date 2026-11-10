import { useEffect, useRef, useState, type ReactNode } from "react";
import Markdown from "react-markdown";

import type { ChatMessage } from "../types";

interface Props {
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
  inputDisabled: boolean;
  onSend: (text: string) => void;
  children?: ReactNode; // slot for the approval card
}

const BUBBLE: Record<ChatMessage["role"], string> = {
  user: "self-end bg-blue-600 text-white whitespace-pre-wrap",
  agent: "self-start bg-slate-800",
  system: "self-center bg-transparent text-xs italic text-slate-400",
};

export function ChatPanel({ messages, loading, error, inputDisabled, onSend, children }: Props) {
  const [text, setText] = useState("");
  const endRef = useRef<HTMLDivElement>(null);
  const hasChildren = Boolean(children);

  // Scroll to the bottom on new messages, while thinking, and when the approval card appears
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, loading, hasChildren]);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="flex flex-col flex-1 min-h-0 rounded-xl border border-slate-800 bg-slate-900/50">
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
        {messages.length === 0 && (
          <p className="m-auto text-sm text-slate-500">
            Ask about your balance, send money, or click an attack above.
          </p>
        )}

        {messages.map((m) => (
          <div key={m.id} className={`max-w-[80%] rounded-2xl px-4 py-2 ${BUBBLE[m.role]}`}>
            {m.role === "agent" ? (
              <div className="space-y-2 [&_strong]:font-semibold [&_ol]:list-decimal [&_ol]:pl-5 [&_ul]:list-disc [&_ul]:pl-5">
                <Markdown>{m.content}</Markdown>
              </div>
            ) : (
              m.content
            )}
          </div>
        ))}

        {loading && (
          <div className="self-start text-sm text-slate-400 animate-pulse">Agent is thinking…</div>
        )}

        {children}

        {error && <div className="text-sm text-red-400">Error: {error}</div>}

        <div ref={endRef} />
      </div>

      <form onSubmit={submit} className="flex gap-2 border-t border-slate-800 p-3">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={inputDisabled}
          placeholder={inputDisabled ? "Approve or decline the transfer first…" : "Type a message…"}
          className="flex-1 rounded-lg bg-slate-800 px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        />
        <button
          disabled={inputDisabled || !text.trim()}
          className="rounded-lg bg-blue-600 px-4 font-medium hover:bg-blue-500 disabled:opacity-40"
        >
          Send
        </button>
      </form>
    </div>
  );
}