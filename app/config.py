from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    company_name: str = "NovaCRM"
    default_agent_name: str = "Ava"
    escalation_sentiment_threshold: float = -0.35
    max_recent_messages_for_context: int = 8

CONFIG = AppConfig()
