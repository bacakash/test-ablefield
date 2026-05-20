from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from app.domain.enums import (
    InteractionChannel,
    LeadStatus,
    MessageRole,
    TicketPriority,
)

@dataclass
class Customer:
    id: str
    full_name: str
    email: str
    company: Optional[str] = None
    phone: Optional[str] = None
    lead_status: LeadStatus = LeadStatus.NEW
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class CRMNote:
    id: str
    customer_id: str
    text: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class SupportTicket:
    id: str
    customer_id: str
    title: str
    description: str
    priority: TicketPriority
    is_open: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None

@dataclass
class ConversationMessage:
    id: str
    customer_id: str
    role: MessageRole
    content: str
    channel: InteractionChannel
    sentiment_score: float
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class AgentReply:
    reply: str
    detected_intent: str
    sentiment_score: float
    should_escalate: bool
    suggested_tags: List[str]
    crm_actions: List[str]
