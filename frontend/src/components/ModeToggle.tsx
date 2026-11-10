import type { Mode } from "../types";

interface Props {
  mode: Mode;
  onChange: (mode: Mode) => void;
}

export function ModeToggle({ mode, onChange }: Props) {
  const options: { value: Mode; label: string; active: string }[] = [
    { value: "naive", label: "Naive (no harness)", active: "bg-red-600" },
    { value: "harnessed", label: "Harnessed", active: "bg-emerald-600" },
  ];
  return (
    <div className="inline-flex rounded-lg bg-slate-800 p-1">
      {options.map((o) => (
        <button
          key={o.value}
          onClick={() => onChange(o.value)}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${
            mode === o.value ? `${o.active} text-white` : "text-slate-400 hover:text-slate-200"
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}