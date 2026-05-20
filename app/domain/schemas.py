from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field

from app.domain.enums import InteractionChannel, LeadStatus, TicketPriority

class CustomerCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    company: Optional[str] = Field(default=None, max_length=120)
    phone: Optional[str] = Field(default=None, max_length=40)

class CustomerResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    company: Optional[str]
    phone: Optional[str]
    lead_status: LeadStatus
    tags: List[str]
    created_at: datetime
    updated_at: datetime

class CustomerMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    channel: InteractionChannel = InteractionChannel.CHAT

class AgentReplyResponse(BaseModel):
    reply: str
    detected_intent: str
    sentiment_score: float
    should_escalate: bool
    suggested_tags: List[str]
    crm_actions: List[str]

class CRMNoteRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)

class TicketCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=160)
    description: str = Field(..., min_length=3, max_length=4000)
    priority: TicketPriority = TicketPriority.MEDIUM

class AnalyticsSummaryResponse(BaseModel):
    total_customers: int
    total_messages: int
    customer_messages: int
    agent_messages: int
    open_tickets: int
    lead_status_distribution: Dict[str, int]
    top_intents: Dict[str, int]
    average_sentiment: float
    escalation_rate_percent: float
    busiest_channels: Dict[str, int]
