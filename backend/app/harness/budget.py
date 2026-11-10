from app.config import get_settings

BUDGET_MESSAGE = (
    "I wasn't able to complete this request safely within my step limit. "
    "Please try again with a simpler request, or contact support."
)


def budget_exceeded(steps: int) -> bool:
    return steps >= get_settings().max_agent_steps