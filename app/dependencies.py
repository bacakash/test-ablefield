from app.config import CONFIG
from app.repositories.memory import (
    InMemoryCRMNoteRepository,
    InMemoryConversationRepository,
    InMemoryCustomerRepository,
    InMemoryTicketRepository,
)
from app.services.agent import CustomerAgentService
from app.services.analytics import AnalyticsService
from app.services.crm import CRMService
from app.services.nlp import IntentClassifier, SentimentAnalyzer, TagSuggester

customer_repo = InMemoryCustomerRepository()
conversation_repo = InMemoryConversationRepository()
note_repo = InMemoryCRMNoteRepository()
ticket_repo = InMemoryTicketRepository()

sentiment_analyzer = SentimentAnalyzer()
intent_classifier = IntentClassifier()
tag_suggester = TagSuggester()

crm_service = CRMService(
    customer_repo=customer_repo,
    note_repo=note_repo,
    ticket_repo=ticket_repo,
)

agent_service = CustomerAgentService(
    crm_service=crm_service,
    conversation_repo=conversation_repo,
    sentiment_analyzer=sentiment_analyzer,
    intent_classifier=intent_classifier,
    tag_suggester=tag_suggester,
    config=CONFIG,
)

analytics_service = AnalyticsService(
    customer_repo=customer_repo,
    conversation_repo=conversation_repo,
    ticket_repo=ticket_repo,
    intent_classifier=intent_classifier,
    config=CONFIG,
)
