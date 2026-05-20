import uuid
from typing import List

from app.config import AppConfig
from app.domain.enums import InteractionChannel, LeadStatus, MessageRole, TicketPriority
from app.domain.models import AgentReply, ConversationMessage
from app.repositories.interfaces import ConversationRepository
from app.services.crm import CRMService
from app.services.nlp import IntentClassifier, SentimentAnalyzer, TagSuggester

class CustomerAgentService:
    def __init__(
        self,
        crm_service: CRMService,
        conversation_repo: ConversationRepository,
        sentiment_analyzer: SentimentAnalyzer,
        intent_classifier: IntentClassifier,
        tag_suggester: TagSuggester,
        config: AppConfig,
    ) -> None:
        self.crm_service = crm_service
        self.conversation_repo = conversation_repo
        self.sentiment_analyzer = sentiment_analyzer
        self.intent_classifier = intent_classifier
        self.tag_suggester = tag_suggester
        self.config = config

    def handle_customer_message(
        self,
        customer_id: str,
        message: str,
        channel: InteractionChannel,
    ) -> AgentReply:
        customer = self.crm_service.get_customer_or_raise(customer_id)
        sentiment_score = self.sentiment_analyzer.score(message)
        intent = self.intent_classifier.classify(message)
        suggested_tags = self.tag_suggester.suggest(intent, sentiment_score)

        self.conversation_repo.add(
            ConversationMessage(
                id=str(uuid.uuid4()),
                customer_id=customer_id,
                role=MessageRole.CUSTOMER,
                content=message,
                channel=channel,
                sentiment_score=sentiment_score,
            )
        )

        should_escalate = sentiment_score <= self.config.escalation_sentiment_threshold
        crm_actions: List[str] = []

        if suggested_tags:
            self.crm_service.add_tags(customer_id, suggested_tags)
            crm_actions.append(f"Applied CRM tags: {', '.join(suggested_tags)}")

        if intent in {"pricing", "demo_request"}:
            self.crm_service.update_lead_status(customer_id, LeadStatus.QUALIFIED)
            crm_actions.append("Lead status updated to qualified")

        if intent == "technical_support":
            ticket = self.crm_service.create_ticket(
                customer_id=customer_id,
                title="Technical support request",
                description=message,
                priority=TicketPriority.HIGH if should_escalate else TicketPriority.MEDIUM,
            )
            crm_actions.append(f"Support ticket created: {ticket.id}")

        if intent == "billing" and should_escalate:
            ticket = self.crm_service.create_ticket(
                customer_id=customer_id,
                title="Billing escalation",
                description=message,
                priority=TicketPriority.HIGH,
            )
            crm_actions.append(f"Billing escalation ticket created: {ticket.id}")

        if intent == "cancellation":
            self.crm_service.add_tags(customer_id, ["retention-follow-up"])
            crm_actions.append("Retention follow-up tag added")

        reply_text = self._build_reply(
            customer_name=customer.full_name,
            intent=intent,
            should_escalate=should_escalate,
            sentiment_score=sentiment_score,
        )

        self.conversation_repo.add(
            ConversationMessage(
                id=str(uuid.uuid4()),
                customer_id=customer_id,
                role=MessageRole.AGENT,
                content=reply_text,
                channel=channel,
                sentiment_score=0.0,
            )
        )

        note = self.crm_service.add_note(
            customer_id,
            f"Intent={intent}; Sentiment={sentiment_score}; Escalate={should_escalate}",
        )
        crm_actions.append(f"CRM note stored: {note.id}")

        return AgentReply(
            reply=reply_text,
            detected_intent=intent,
            sentiment_score=sentiment_score,
            should_escalate=should_escalate,
            suggested_tags=suggested_tags,
            crm_actions=crm_actions,
        )

    def _build_reply(
        self,
        customer_name: str,
        intent: str,
        should_escalate: bool,
        sentiment_score: float,
    ) -> str:
        prefix = f"Hi {customer_name},"

        if should_escalate:
            return (
                f"{prefix} I understand this needs attention. "
                "I have logged it for priority review and a team member will follow up."
            )

        if intent == "pricing":
            return (
                f"{prefix} I can help with pricing. "
                "Please share your team size and main use case so I can guide you to the best plan."
            )

        if intent == "demo_request":
            return (
                f"{prefix} I can help arrange a product demo. "
                "Please share your preferred time window and the workflows you want to review."
            )

        if intent == "technical_support":
            return (
                f"{prefix} I noted the issue and opened a support request. "
                "Please send any screenshots, error text, or steps to reproduce it."
            )

        if intent == "billing":
            return (
                f"{prefix} I can help check the billing concern. "
                "Please share the invoice number or the billing period you are referring to."
            )

        if intent == "cancellation":
            return (
                f"{prefix} I’m sorry to hear that. "
                "I can help review options or connect you with the retention team."
            )

        if intent == "feature_question":
            return (
                f"{prefix} I can help explain the product capabilities. "
                "Please tell me which workflow or integration you want to evaluate."
            )

        if intent == "general_greeting":
            return f"{prefix} welcome to NovaCRM. How can I help today?"

        tone_hint = "Thanks for reaching out." if sentiment_score >= 0 else "I understand your concern."
        return f"{prefix} {tone_hint} Please share a bit more detail so I can assist accurately."
