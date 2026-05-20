from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.domain.models import CRMNote, ConversationMessage, Customer, SupportTicket

class InMemoryCustomerRepository:
    def __init__(self) -> None:
        self._items: Dict[str, Customer] = {}

    def create(self, customer: Customer) -> Customer:
        self._items[customer.id] = customer
        return customer

    def get(self, customer_id: str) -> Optional[Customer]:
        return self._items.get(customer_id)

    def update(self, customer: Customer) -> Customer:
        customer.updated_at = datetime.now(timezone.utc)
        self._items[customer.id] = customer
        return customer

    def list_all(self) -> List[Customer]:
        return list(self._items.values())

class InMemoryConversationRepository:
    def __init__(self) -> None:
        self._messages: List[ConversationMessage] = []

    def add(self, message: ConversationMessage) -> ConversationMessage:
        self._messages.append(message)
        return message

    def list_by_customer(self, customer_id: str) -> List[ConversationMessage]:
        return [m for m in self._messages if m.customer_id == customer_id]

    def list_all(self) -> List[ConversationMessage]:
        return list(self._messages)

class InMemoryCRMNoteRepository:
    def __init__(self) -> None:
        self._notes: List[CRMNote] = []

    def add(self, note: CRMNote) -> CRMNote:
        self._notes.append(note)
        return note

    def list_by_customer(self, customer_id: str) -> List[CRMNote]:
        return [n for n in self._notes if n.customer_id == customer_id]

class InMemoryTicketRepository:
    def __init__(self) -> None:
        self._tickets: Dict[str, SupportTicket] = {}

    def create(self, ticket: SupportTicket) -> SupportTicket:
        self._tickets[ticket.id] = ticket
        return ticket

    def list_by_customer(self, customer_id: str) -> List[SupportTicket]:
        return [t for t in self._tickets.values() if t.customer_id == customer_id]

    def list_all(self) -> List[SupportTicket]:
        return list(self._tickets.values())
