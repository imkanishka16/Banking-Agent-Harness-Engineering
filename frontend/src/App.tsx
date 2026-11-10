import { ApprovalCard } from "./components/ApprovalCard";
import { BankPanel } from "./components/BankPanel";
import { ChatPanel } from "./components/ChatPanel";
import { ModeToggle } from "./components/ModeToggle";
import { ScenarioButtons } from "./components/ScenarioButtons";
import { TracePanel } from "./components/TracePanel";
import { useChat } from "./hooks/useChat";

const BANNER = {
  naive: {
    cls: "bg-red-500/10 text-red-300 border-red-500/30",
    text: "NAIVE: LLM + tools, nothing in between. Safety depends entirely on the model's judgement.",
  },
  harnessed: {
    cls: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
    text: "HARNESSED: session-bound tools · deterministic policy · daily limit · content guard · human approval · step budget · audit trace",
  },
};

export default function App() {
  const chat = useChat();
  const banner = BANNER[chat.mode];
  const busy = chat.loading;
  const waitingForApproval = Boolean(chat.pendingApproval);

  return (
    <div className="h-screen flex flex-col bg-slate-950 text-slate-100">
      <header className="flex items-center gap-4 border-b border-slate-800 px-6 py-3">
        <h1 className="text-lg font-semibold">
          🏦 Banking Agent{" "}
          <span className="font-normal text-slate-400">· Harness Engineering demo</span>
        </h1>
        <ModeToggle mode={chat.mode} onChange={chat.setMode} />
        <button
          onClick={chat.reset}
          disabled={busy}
          className="ml-auto rounded-lg bg-slate-800 px-3 py-1.5 text-sm hover:bg-slate-700 disabled:opacity-40"
        >
          Reset bank
        </button>
      </header>

      <div className={`mx-4 mt-3 rounded-lg border px-4 py-2 text-sm ${banner.cls}`}>
        {banner.text}
      </div>

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-3 lg:grid-rows-[minmax(0,1fr)] gap-4 p-4 min-h-0">
        <section className="lg:col-span-2 flex flex-col gap-3 min-h-0">
          <ScenarioButtons onPick={chat.send} disabled={busy || waitingForApproval} />

          <ChatPanel
            messages={chat.messages}
            loading={busy}
            error={chat.error}
            inputDisabled={busy || waitingForApproval}
            onSend={chat.send}
          >
            {chat.pendingApproval && (
              <ApprovalCard
                approval={chat.pendingApproval}
                onDecide={chat.decide}
                disabled={busy}
              />
            )}
          </ChatPanel>
        </section>

        <aside className="flex flex-col gap-4 min-h-0">
          <BankPanel bank={chat.bank} />
          <TracePanel events={chat.events} mode={chat.mode} />
        </aside>
      </main>
    </div>
  );
}