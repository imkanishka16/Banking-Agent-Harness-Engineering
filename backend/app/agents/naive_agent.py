from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.bank.mock_bank import bank
from app.config import get_settings
from app.tools.banking_tools import ALL_TOOLS

NAIVE_SYSTEM_PROMPT = """You are a helpful banking assistant for a retail bank.
The logged-in customer's account ID is ACC-1001.
Use the available tools to answer questions and complete requests."""


def build_naive_agent(checkpointer=None):
    """Stage 1: LLM + tools, no harness. Safety depends entirely on the model."""
    s = get_settings()
    llm = ChatOpenAI(model=s.openai_model, api_key=s.openai_api_key, temperature=0)
    return create_agent(model=llm, tools=ALL_TOOLS, system_prompt=NAIVE_SYSTEM_PROMPT,
                        checkpointer=checkpointer)


def print_trace(messages) -> None:
    """Show what the agent actually did, not just what it said."""
    for m in messages:
        if isinstance(m, AIMessage) and m.tool_calls:
            for tc in m.tool_calls:
                print(f"  [tool call]   {tc['name']}({tc['args']})")
        elif isinstance(m, ToolMessage):
            print(f"  [tool result] {str(m.content)[:200]}")
        elif isinstance(m, AIMessage) and m.content:
            print(f"\nAgent: {m.content}\n")


def chat_loop() -> None:
    agent = build_naive_agent()
    history: list = []
    print("=== Stage 1: NAIVE agent (no harness) ===")
    print("Commands: 'exit' to quit, 'reset' to restore bank data.\n")

    while True:
        user = input("You: ").strip()
        if not user:
            continue
        if user.lower() == "exit":
            break
        if user.lower() == "reset":
            bank.reset()
            history.clear()
            print("[bank data and conversation reset]\n")
            continue

        history.append({"role": "user", "content": user})
        result = agent.invoke({"messages": history})
        print_trace(result["messages"][len(history):])
        history = result["messages"]


if __name__ == "__main__":
    chat_loop()