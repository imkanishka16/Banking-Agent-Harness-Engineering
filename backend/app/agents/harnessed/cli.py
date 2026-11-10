from langgraph.types import Command

from app.agents.harnessed.graph import build_harnessed_agent
from app.agents.naive_agent import print_trace
from app.bank.mock_bank import bank
from app.tools.session_tools import Session


def chat_loop() -> None:
    session = Session(account_id="ACC-1001", customer_name="Demo Customer")
    agent = build_harnessed_agent(session)
    thread_no = 1
    print("=== Stage 2: HARNESSED agent ===")
    print("Commands: 'exit' to quit, 'reset' to restore bank data.\n")

    while True:
        user = input("You: ").strip()
        if not user:
            continue
        if user.lower() == "exit":
            break
        if user.lower() == "reset":
            bank.reset()
            thread_no += 1  # new thread = fresh conversation
            print("[bank data and conversation reset]\n")
            continue

        config = {"configurable": {"thread_id": f"cli-{thread_no}"}}
        seen = len(agent.get_state(config).values.get("messages", []))

        result = agent.invoke(
            {"messages": [{"role": "user", "content": user}], "steps": 0}, config
        )
        while True:
            print_trace(result["messages"][seen:])
            seen = len(result["messages"])
            if "__interrupt__" not in result:
                break
            req = result["__interrupt__"][0].value
            print(f"\n  [APPROVAL REQUIRED] {req['message']}")
            answer = input("  Approve? (y/n): ").strip().lower()
            result = agent.invoke(Command(resume={"approved": answer == "y"}), config)


if __name__ == "__main__":
    chat_loop()