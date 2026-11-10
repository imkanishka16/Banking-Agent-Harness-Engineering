from fastapi import APIRouter, HTTPException

from app.agents import runner
from app.api.schemas import ApproveRequest, ChatRequest, ChatResponse, TraceEvent
from app.bank.mock_bank import bank
from app.harness.tracer import tracer

router = APIRouter(prefix="/api")


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    return runner.chat(req.mode, req.thread_id, req.message)


@router.post("/approve", response_model=ChatResponse)
def approve(req: ApproveRequest):
    try:
        return runner.approve(req.thread_id, req.approved)
    except runner.NoPendingApproval as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/traces/{thread_id}", response_model=list[TraceEvent])
def traces(thread_id: str):
    return tracer.get(thread_id)


@router.get("/bank")
def bank_state():
    """Ground truth for the UI: what actually happened to the money."""
    return {
        "accounts": [a.model_dump() for a in bank.accounts.values()],
        "transactions": [t.model_dump(mode="json") for t in bank.transactions.values()],
    }


@router.post("/reset")
def reset():
    bank.reset()
    tracer.clear()
    runner.reset_agents()
    return {"status": "reset"}