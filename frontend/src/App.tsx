import { useState } from "react";

import { useChat } from "./hooks/useChat";

export default function App() {
  const chat = useChat();
  const [text, setText] = useState("");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-4">
      <div className="flex items-center gap-2">
        {(["naive", "harnessed"] as const).map((m) => (
          <button
            key={m}
            onClick={() => chat.setMode(m)}
            className={`px-3 py-1 rounded ${chat.mode === m ? "bg-blue-600" : "bg-slate-800"}`}
          >
            {m}
          </button>
        ))}
        <button onClick={chat.reset} className="ml-auto px-3 py-1 rounded bg-slate-800">
          Reset
        </button>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          chat.send(text);
          setText("");
        }}
        className="flex gap-2"
      >
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Send 5000 to Nimal Perera"
          className="flex-1 bg-slate-800 px-3 py-2 rounded"
        />
        <button className="bg-blue-600 px-4 rounded">Send</button>
      </form>

      {chat.pendingApproval && (
        <div className="border border-amber-500 rounded p-3 space-x-2">
          <span>{chat.pendingApproval.message}</span>
          <button onClick={() => chat.decide(true)} className="bg-green-700 px-3 py-1 rounded">Approve</button>
          <button onClick={() => chat.decide(false)} className="bg-red-700 px-3 py-1 rounded">Decline</button>
        </div>
      )}
      {chat.loading && <p className="text-slate-400">Thinking…</p>}
      {chat.error && <p className="text-red-400">{chat.error}</p>}

      <pre className="text-xs bg-slate-900 p-3 rounded overflow-auto">
        {JSON.stringify(
          {
            messages: chat.messages,
            events: chat.events.map((e) => e.type),
            balances: chat.bank?.accounts.map((a) => `${a.account_id}: ${a.balance}`),
          },
          null,
          2,
        )}
      </pre>
    </div>
  );
}