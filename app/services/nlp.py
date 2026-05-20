import re
from collections import defaultdict
from typing import Dict, List, Tuple

class SentimentAnalyzer:
    POSITIVE_WORDS = {
        "great", "good", "thanks", "helpful", "happy",
        "excellent", "love", "resolved", "fast", "easy",
    }

    NEGATIVE_WORDS = {
        "bad", "angry", "frustrated", "slow", "broken",
        "problem", "issue", "refund", "cancel", "complaint",
        "terrible", "not working",
    }

    def score(self, text: str) -> float:
        normalized = text.lower()
        tokens = re.findall(r"[a-zA-Z']+", normalized)
        if not tokens:
            return 0.0

        positive_hits = sum(1 for token in tokens if token in self.POSITIVE_WORDS)
        negative_hits = sum(1 for token in tokens if token in self.NEGATIVE_WORDS)

        if "not working" in normalized:
            negative_hits += 1

        raw = positive_hits - negative_hits
        denominator = max(len(tokens) ** 0.5, 1)
        score = raw / denominator
        return max(-1.0, min(1.0, round(score, 3)))

class IntentClassifier:
    INTENT_PATTERNS: Dict[str, Tuple[str, ...]] = {
        "pricing": ("price", "pricing", "cost", "quote", "plan"),
        "demo_request": ("demo", "book a call", "schedule", "show me"),
        "technical_support": ("error", "bug", "not working", "issue", "problem"),
        "billing": ("invoice", "payment", "charged", "refund", "billing"),
        "cancellation": ("cancel", "terminate", "stop subscription"),
        "feature_question": ("feature", "integration", "api", "workflow"),
        "general_greeting": ("hello", "hi", "hey", "good morning", "good evening"),
    }

    def classify(self, text: str) -> str:
        normalized = text.lower()
        scores: Dict[str, int] = defaultdict(int)

        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in normalized:
                    scores[intent] += 1

        if not scores:
            return "general_question"

        return max(scores.items(), key=lambda pair: pair[1])[0]

class TagSuggester:
    TAG_RULES: Dict[str, List[str]] = {
        "pricing": ["sales-interest", "pricing"],
        "demo_request": ["sales-interest", "demo-request"],
        "technical_support": ["support", "technical"],
        "billing": ["finance", "billing"],
        "cancellation": ["churn-risk", "retention"],
        "feature_question": ["product-interest"],
    }

    def suggest(self, intent: str, sentiment_score: float) -> List[str]:
        tags = list(self.TAG_RULES.get(intent, []))
        if sentiment_score < -0.25:
            tags.append("negative-sentiment")
        if sentiment_score > 0.25:
            tags.append("positive-sentiment")
        return sorted(set(tags))
