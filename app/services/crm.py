import uuid

from fastapi import HTTPException

from app.domain.enums import LeadStatus, TicketPriority
from app.domain.models import CRMNote, Customer, SupportTicket
from app.domain.schemas import CustomerCreateRequest
from app.repositories.interfaces import CRMNoteRepository, CustomerRepository, TicketRepository

class CRMService:
    def __init__(
        self,
        customer_repo: CustomerRepository,
        note_repo: CRMNoteRepository,
        ticket_repo: TicketRepository,
    ) -> None:
        self.customer_repo = customer_repo
        self.note_repo = note_repo
        self.ticket_repo = ticket_repo

    def create_customer(self, request: CustomerCreateRequest) -> Customer:
        customer = Customer(
            id=str(uuid.uuid4()),
            full_name=request.full_name,
            email=str(request.email),
            company=request.company,
            phone=request.phone,
        )
        return self.customer_repo.create(customer)

    def get_customer_or_raise(self, customer_id: str) -> Customer:
        customer = self.customer_repo.get(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer

    def add_tags(self, customer_id: str, tags: list[str]) -> Customer:
        customer = self.get_customer_or_raise(customer_id)
        customer.tags = sorted(set(customer.tags).union(tags))
        return self.customer_repo.update(customer)

    def update_lead_status(self, customer_id: str, status: LeadStatus) -> Customer:
        customer = self.get_customer_or_raise(customer_id)
        customer.lead_status = status
        return self.customer_repo.update(customer)

    def add_note(self, customer_id: str, note_text: str) -> CRMNote:
        self.get_customer_or_raise(customer_id)
        note = CRMNote(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            text=note_text,
        )
        return self.note_repo.add(note)

    def create_ticket(
        self,
        customer_id: str,
        title: str,
        description: str,
        priority: TicketPriority,
    ) -> SupportTicket:
        self.get_customer_or_raise(customer_id)
        ticket = SupportTicket(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            title=title,
            description=description,
            priority=priority,
        )
        return self.ticket_repo.create(ticket)
