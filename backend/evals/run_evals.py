"""Run every scenario against both agents and print a scorecard.

Usage:
    python -m evals.run_evals            # 1 run per scenario
    python -m evals.run_evals --runs 3   # repeat to expose LLM non-determinism
"""
import argparse
import uuid
from datetime import datetime
from pathlib import Path

from app.agents import runner
from app.bank.mock_bank import bank
from app.config import get_settings
from app.harness.tracer import tracer
from evals.scenarios import SCENARIOS, Outcome, Scenario

MODES = ["naive", "harnessed"]
MAX_APPROVALS_PER_TURN = 5


def run_scenario(scenario: Scenario, mode: str) -> tuple[bool, str]:
    bank.reset()
    tracer.clear()
    runner.reset_agents()
    thread_id = f"eval-{scenario.id}-{uuid.uuid4().hex[:6]}"
    replies: list[str] = []

    try:
        for turn in scenario.turns:
            out = runner.chat(mode, thread_id, turn)
            approvals = 0
            while out["status"] == "awaiting_approval" and approvals < MAX_APPROVALS_PER_TURN:
                # Simulated careless user: approves EVERYTHING.
                # Safety must not depend on the human paying attention.
                out = runner.approve(thread_id, approved=True)
                approvals += 1
            if out["reply"]:
                replies.append(out["reply"])
    except Exception as e:  # an eval run must never crash the whole suite
        return False, f"error: {type(e).__name__}: {e}"

    outcome = Outcome(
        replies=replies,
        events=tracer.get(thread_id),
        transactions=list(bank.transactions.values()),
        balances={a.account_id: a.balance for a in bank.accounts.values()},
    )
    return scenario.check(outcome)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()

    results: dict[str, dict[str, list[tuple[bool, str]]]] = {}
    for s in SCENARIOS:
        results[s.id] = {}
        for mode in MODES:
            print(f"  running {s.id:<24} [{mode}] ...")
            results[s.id][mode] = [run_scenario(s, mode) for _ in range(args.runs)]

    # ---------- console scorecard ----------
    def score(sid, mode):
        runs = results[sid][mode]
        return f"{sum(p for p, _ in runs)}/{len(runs)}"

    print("\n" + "=" * 68)
    print(f"{'Scenario':<26}{'Category':<12}{'Naive':>12}{'Harnessed':>14}")
    print("-" * 68)
    for s in SCENARIOS:
        print(f"{s.id:<26}{s.category:<12}{score(s.id, 'naive'):>12}{score(s.id, 'harnessed'):>14}")
    print("-" * 68)
    for cat in ("safety", "capability"):
        row = []
        for mode in MODES:
            runs = [r for s in SCENARIOS if s.category == cat for r in results[s.id][mode]]
            row.append(f"{sum(p for p, _ in runs)}/{len(runs)}")
        print(f"{cat.upper() + ' TOTAL':<38}{row[0]:>12}{row[1]:>14}")
    print("=" * 68)

    print("\nFailures:")
    for s in SCENARIOS:
        for mode in MODES:
            for passed, detail in results[s.id][mode]:
                if not passed:
                    print(f"  [{mode:<9}] {s.id}: {detail}")

    # ---------- markdown report for the README ----------
    lines = [
        "# Eval results",
        "",
        f"Model: `{get_settings().openai_model}` | Runs per scenario: {args.runs} | "
        f"{datetime.now():%Y-%m-%d %H:%M}",
        "",
        "| Scenario | Category | What it tests | Naive | Harnessed |",
        "|---|---|---|---|---|",
    ]
    for s in SCENARIOS:
        lines.append(f"| `{s.id}` | {s.category} | {s.description} | "
                     f"{score(s.id, 'naive')} | {score(s.id, 'harnessed')} |")
    out_file = Path(__file__).parent / "results.md"
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSaved {out_file}")


if __name__ == "__main__":
    main()