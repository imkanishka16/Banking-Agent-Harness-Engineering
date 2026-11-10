from typing import Any, Literal

from pydantic import BaseModel, Field

Mode = Literal["naive", "harnessed"]


class ChatRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=2000)  # input size limit = a harness control too
    mode: Mode = "harnessed"


class ApproveRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=64)
    approved: bool


class TraceEvent(BaseModel):
    ts: str
    thread_id: str
    mode: str
    type: str
    data: dict[str, Any]


class ChatResponse(BaseModel):
    thread_id: str
    mode: Mode
    status: Literal["completed", "awaiting_approval"]
    reply: str | None
    approval: dict[str, Any] | None
    events: list[TraceEvent]