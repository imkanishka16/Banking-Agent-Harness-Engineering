import type { ApprovalRequest } from "../types";

interface Props {
  approval: ApprovalRequest;
  onDecide: (approved: boolean) => void;
  disabled: boolean;
}

export function ApprovalCard({ approval, onDecide, disabled }: Props) {
  const rows = [
    ["To", approval.beneficiary_name],
    ["Bank", approval.bank_name],
    ["Account", approval.account_number],
    ["Reference", approval.reference || "-"],
  ];
  return (
    <div className="rounded-xl border border-amber-500/60 bg-amber-500/10 p-4 space-y-3">
      <div className="text-sm font-semibold text-amber-300">
        ✋ Approval required: the agent wants to move money
      </div>
      <div className="text-2xl font-bold">
        {approval.amount.toLocaleString()} {approval.currency}
      </div>
      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
        {rows.map(([k, v]) => (
          <div key={k} className="contents">
            <dt className="text-slate-400">{k}</dt>
            <dd className="font-medium">{v}</dd>
          </div>
        ))}
      </dl>
      <p className="text-xs text-slate-400">
        These details come from bank records, not from the AI's text.
      </p>
      <div className="flex gap-2">
        <button
          disabled={disabled}
          onClick={() => onDecide(true)}
          className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 font-medium disabled:opacity-40"
        >
          Approve
        </button>
        <button
          disabled={disabled}
          onClick={() => onDecide(false)}
          className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 font-medium disabled:opacity-40"
        >
          Decline
        </button>
      </div>
    </div>
  );
}