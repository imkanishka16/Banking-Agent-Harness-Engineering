import { useState } from "react";

import type { EventType, Mode, TraceEvent } from "../types";

const STYLE: Record<EventType, { icon: string; cls: string; harness?: boolean }> = {
  user_message: { icon: "💬", cls: "text-slate-400" },
  tool_call: { icon: "🔧", cls: "text-sky-300" },
  tool_result: { icon: "📦", cls: "text-slate-400" },
  agent_reply: { icon: "🤖", cls: "text-slate-300" },
  policy_block: { icon: "⛔", cls: "text-red-300", harness: true },
  guard_finding: { icon: "🛡️", cls: "text-amber-300", harness: true },
  approval_requested: { icon: "✋", cls: "text-amber-300", harness: true },
  approval_decision: { icon: "👤", cls: "text-emerald-300", harness: true },
  transfer_declined: { icon: "🚫", cls: "text-slate-300", harness: true },
  budget_exceeded: { icon: "⏱️", cls: "text-red-300", harness: true },
};

function describe(e: TraceEvent): string {
  const d = e.data;
  const short = (v: unknown) => {
    const s = typeof v === "string" ? v : JSON.stringify(v);
    return s.length > 110 ? s.slice(0, 110) + "…" : s;
  };
  switch (e.type) {
    case "user_message":
    case "agent_reply":
      return short(d.content);
    case "tool_call":
      return `${d.name}(${short(d.args)})`;
    case "tool_result":
      return `${d.tool} → ${short(d.result)}`;
    case "policy_block":
      return `${d.code}: ${d.reason}`;
    case "guard_finding":
      return short(d.notice);
    case "approval_requested":
      return short(d.message);
    case "approval_decision":
      return d.approved ? "Customer approved" : "Customer declined";
    case "transfer_declined":
      return "Transfer not executed";
    case "budget_exceeded":
      return "Step budget exceeded, run stopped";
  }
}

export function TracePanel({ events, mode }: { events: TraceEvent[]; mode: Mode }) {
  const [harnessOnly, setHarnessOnly] = useState(false);
  const shown = harnessOnly ? events.filter((e) => STYLE[e.type].harness) : events;

  return (
    <div className="flex flex-col flex-1 min-h-0 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xs uppercase tracking-wide text-slate-500">Harness trace</h2>
        <label className="flex items-center gap-1 text-xs text-slate-400">
          <input type="checkbox" checked={harnessOnly} onChange={(e) => setHarnessOnly(e.target.checked)} />
          harness events only
        </label>
      </div>

      {mode === "naive" && (
        <p className="mb-2 rounded bg-red-500/10 px-2 py-1 text-xs text-red-300">
          No harness: nothing checks these tool calls before they run.
        </p>
      )}

      <div className="flex-1 overflow-y-auto space-y-1">
        {shown.length === 0 && <p className="text-xs text-slate-500">No events yet.</p>}
        {shown.map((e, i) => {
          const s = STYLE[e.type];
          return (
            <div
              key={i}
              className={`text-xs font-mono rounded px-2 py-1 ${s.cls} ${s.harness ? "bg-slate-800 border-l-2 border-current" : ""}`}
            >
              <span className="mr-1">{s.icon}</span>
              <span className="font-semibold">{e.type}</span> {describe(e)}
            </div>
          );
        })}
      </div>
    </div>
  );
}