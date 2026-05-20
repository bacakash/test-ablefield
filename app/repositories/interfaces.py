from typing import List, Optional, Protocol

from app.domain.models import CRMNote, ConversationMessage, Customer, SupportTicket

class CustomerRepository(Protocol):
    def create(self, customer: Customer) -> Customer:
        ...

    def get(self, customer_id: str) -> Optional[Customer]:
        ...

    def update(self, customer: Customer) -> Customer:
        ...

    def list_all(self) -> List[Customer]:
        ...

class ConversationRepository(Protocol):
    def add(self, message: ConversationMessage) -> ConversationMessage:
        ...

    def list_by_customer(self, customer_id: str) -> List[ConversationMessage]:
        ...

    def list_all(self) -> List[ConversationMessage]:
        ...

class CRMNoteRepository(Protocol):
    def add(self, note: CRMNote) -> CRMNote:
        ...

    def list_by_customer(self, customer_id: str) -> List[CRMNote]:
        ...

class TicketRepository(Protocol):
    def create(self, ticket: SupportTicket) -> SupportTicket:
        ...

    def list_by_customer(self, customer_id: str) -> List[SupportTicket]:
        ...

    def list_all(self) -> List[SupportTicket]:
        ...
