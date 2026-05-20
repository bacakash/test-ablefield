from collections import Counter

from app.config import AppConfig
from app.domain.enums import MessageRole
from app.domain.schemas import AnalyticsSummaryResponse
from app.repositories.interfaces import ConversationRepository, CustomerRepository, TicketRepository
from app.services.nlp import IntentClassifier

class AnalyticsService:
    def __init__(
        self,
        customer_repo: CustomerRepository,
        conversation_repo: ConversationRepository,
        ticket_repo: TicketRepository,
        intent_classifier: IntentClassifier,
        config: AppConfig,
    ) -> None:
        self.customer_repo = customer_repo
        self.conversation_repo = conversation_repo
        self.ticket_repo = ticket_repo
        self.intent_classifier = intent_classifier
        self.config = config

    def build_summary(self) -> AnalyticsSummaryResponse:
        customers = self.customer_repo.list_all()
        messages = self.conversation_repo.list_all()
        tickets = self.ticket_repo.list_all()

        customer_messages = [m for m in messages if m.role == MessageRole.CUSTOMER]
        agent_messages = [m for m in messages if m.role == MessageRole.AGENT]

        lead_status_distribution = Counter(c.lead_status.value for c in customers)
        busiest_channels = Counter(m.channel.value for m in messages)
        open_tickets = sum(1 for ticket in tickets if ticket.is_open)

        detected_intents = Counter(
            self.intent_classifier.classify(message.content)
            for message in customer_messages
        )

        average_sentiment = (
            sum(m.sentiment_score for m in customer_messages) / len(customer_messages)
            if customer_messages
            else 0.0
        )

        escalations = sum(
            1
            for message in customer_messages
            if message.sentiment_score <= self.config.escalation_sentiment_threshold
        )
        escalation_rate_percent = (
            escalations / len(customer_messages) * 100 if customer_messages else 0.0
        )

        return AnalyticsSummaryResponse(
            total_customers=len(customers),
            total_messages=len(messages),
            customer_messages=len(customer_messages),
            agent_messages=len(agent_messages),
            open_tickets=open_tickets,
            lead_status_distribution=dict(lead_status_distribution),
            top_intents=dict(detected_intents),
            average_sentiment=round(average_sentiment, 3),
            escalation_rate_percent=round(escalation_rate_percent, 2),
            busiest_channels=dict(busiest_channels),
        )
