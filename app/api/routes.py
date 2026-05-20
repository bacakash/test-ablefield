from fastapi import APIRouter

from app.dependencies import analytics_service, conversation_repo, crm_service, agent_service
from app.domain.schemas import (
    AgentReplyResponse,
    AnalyticsSummaryResponse,
    CRMNoteRequest,
    CustomerCreateRequest,
    CustomerMessageRequest,
    CustomerResponse,
    TicketCreateRequest,
)

router = APIRouter()

@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "customer-ai-crm-agent"}

@router.post("/customers", response_model=CustomerResponse)
def create_customer(request: CustomerCreateRequest) -> CustomerResponse:
    customer = crm_service.create_customer(request)
    return CustomerResponse(**customer.__dict__)

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str) -> CustomerResponse:
    customer = crm_service.get_customer_or_raise(customer_id)
    return CustomerResponse(**customer.__dict__)

@router.post("/customers/{customer_id}/notes")
def create_note(customer_id: str, request: CRMNoteRequest) -> dict[str, str]:
    note = crm_service.add_note(customer_id, request.text)
    return {"note_id": note.id, "message": "CRM note created"}

@router.post("/customers/{customer_id}/tickets")
def create_ticket(customer_id: str, request: TicketCreateRequest) -> dict[str, str]:
    ticket = crm_service.create_ticket(
        customer_id=customer_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
    )
    return {"ticket_id": ticket.id, "message": "Support ticket created"}

@router.post("/conversations/{customer_id}/message", response_model=AgentReplyResponse)
def customer_message(
    customer_id: str,
    request: CustomerMessageRequest,
) -> AgentReplyResponse:
    reply = agent_service.handle_customer_message(
        customer_id=customer_id,
        message=request.message,
        channel=request.channel,
    )
    return AgentReplyResponse(**reply.__dict__)

@router.get("/conversations/{customer_id}")
def list_conversation(customer_id: str) -> dict[str, list[dict[str, object]]]:
    crm_service.get_customer_or_raise(customer_id)
    messages = conversation_repo.list_by_customer(customer_id)
    return {
        "messages": [
            {
                "id": message.id,
                "role": message.role.value,
                "content": message.content,
                "channel": message.channel.value,
                "sentiment_score": message.sentiment_score,
                "created_at": message.created_at,
            }
            for message in messages
        ]
    }

@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
def analytics_summary() -> AnalyticsSummaryResponse:
    return analytics_service.build_summary()
