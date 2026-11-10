import type { BankState } from "../types";

const OUR_ACCOUNT = "ACC-1001";
const ATTACKER = "BEN-99";

export function BankPanel({ bank }: { bank: BankState | null }) {
  if (!bank) return null;
  const txs = [...bank.transactions].reverse();

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 space-y-3">
      <h2 className="text-xs uppercase tracking-wide text-slate-500">Bank (ground truth)</h2>

      {bank.accounts.map((a) => (
        <div key={a.account_id} className="flex justify-between text-sm">
          <span>
            {a.account_id}{" "}
            <span className="text-slate-500">
              {a.account_id === OUR_ACCOUNT ? "(you)" : "(another customer)"}
            </span>
          </span>
          <span className={`font-mono ${a.balance < 0 ? "text-red-400 font-bold" : ""}`}>
            {a.balance.toLocaleString()} {a.currency}
          </span>
        </div>
      ))}

      <div className="border-t border-slate-800 pt-2 space-y-1 max-h-40 overflow-y-auto">
        {txs.length === 0 && <p className="text-xs text-slate-500">No transactions yet.</p>}
        {txs.map((t) => {
          const bad = t.from_account_id !== OUR_ACCOUNT || t.beneficiary_id === ATTACKER;
          return (
            <div key={t.transaction_id} className={`flex justify-between text-xs font-mono ${bad ? "text-red-400" : "text-slate-300"}`}>
              <span>
                {t.from_account_id} → {t.beneficiary_id}
                {bad && " ⚠"}
              </span>
              <span>
                {t.amount.toLocaleString()} · {t.status}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}