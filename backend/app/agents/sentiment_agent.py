import json
from app.agents.state import AgentState
from app.agents.llm_helper import llm_helper
from app.core.config import settings
from app.core.logging import logger

class SentimentAgent:
    """Analyzes customer sentiment and determines if human escalation is triggered."""

    SYSTEM_PROMPT = """You are the Sentiment and Emotion Analysis Agent.
Analyze the user's emotional state, satisfaction, and frustration level in this customer support context.

Provide:
1. "sentiment_label": one of ["positive", "neutral", "frustrated", "angry"]
2. "sentiment_score": float between 0.0 (extreme anger/distress) and 1.0 (delighted/happy). Neutral is 0.5.
3. "escalation_required": boolean. Set true if sentiment_score <= 0.35, or if the user is furious, threatening, or demanding a manager.
4. "reason": short summary of detected emotion.

Respond ONLY in JSON format:
{"sentiment_label": "...", "sentiment_score": 0.0, "escalation_required": false, "reason": "..."}
"""

    async def run(self, state: AgentState) -> AgentState:
        trajectory = list(state.get("agent_trajectory", []))
        trajectory.append("SentimentAgent")
        user_message = state["user_message"].strip()
        lower_msg = user_message.lower()

        # Heuristic baseline
        sentiment_label = "neutral"
        sentiment_score = 0.5
        escalation_required = False

        # Negative & frustrated triggers
        frustrated_words = [
            "angry", "frustrated", "horrible", "terrible", "worst", "hate",
            "ridiculous", "useless", "scam", "fraud", "broken", "waste of money",
            "unacceptable", "disaster", "money back", "sue", "legal", "cheat"
        ]
        positive_words = [
            "thank", "thanks", "great", "awesome", "perfect", "good", "helpful", "love", "excellent"
        ]

        neg_hits = sum(1 for w in frustrated_words if w in lower_msg)
        pos_hits = sum(1 for w in positive_words if w in lower_msg)

        if neg_hits > 0:
            sentiment_score = max(0.1, 0.45 - (neg_hits * 0.15))
            sentiment_label = "angry" if sentiment_score < 0.25 else "frustrated"
        elif pos_hits > 0:
            sentiment_score = min(0.95, 0.6 + (pos_hits * 0.15))
            sentiment_label = "positive"
        else:
            sentiment_score = 0.5
            sentiment_label = "neutral"

        if state.get("intent") in ["greeting", "casual_chat", "session_query"]:
            return {
                **state,
                "sentiment_label": "positive" if state.get("intent") != "session_query" else "neutral",
                "sentiment_score": 0.85 if state.get("intent") != "session_query" else 0.50,
                "escalation_required": False,
                "agent_trajectory": trajectory
            }

        if state.get("intent") == "out_of_domain":
            return {
                **state,
                "sentiment_label": "neutral",
                "sentiment_score": 0.50,
                "escalation_required": False,
                "agent_trajectory": trajectory
            }

        if state.get("intent") in ["escalation_request", "complaint"]:
            escalation_required = True
            sentiment_score = min(sentiment_score, 0.3)
            sentiment_label = "frustrated" if sentiment_label == "neutral" else sentiment_label
        elif sentiment_score <= settings.SENTIMENT_ESCALATION_THRESHOLD:
            escalation_required = True

        # Refine with LLM if available and message has emotional indicators
        if llm_helper.client and (neg_hits > 0 or pos_hits > 0 or len(lower_msg.split()) > 10):
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"User Message: {user_message}\nCurrent History: {state.get('history', [])[-2:]}"}
            ]
            res = await llm_helper.generate_chat_completion(messages, response_format={"type": "json_object"})
            if res:
                try:
                    data = json.loads(res)
                    sentiment_label = data.get("sentiment_label", sentiment_label)
                    sentiment_score = float(data.get("sentiment_score", sentiment_score))
                    escalation_required = bool(data.get("escalation_required", escalation_required))
                except Exception as e:
                    logger.warning(f"Error parsing sentiment LLM response: {e}")

        logger.info(f"[SentimentAgent] Score: {sentiment_score:.2f}, Label: {sentiment_label}, Escalation: {escalation_required}")
        return {
            **state,
            "sentiment_label": sentiment_label,
            "sentiment_score": round(sentiment_score, 2),
            "escalation_required": escalation_required,
            "agent_trajectory": trajectory
        }

sentiment_agent = SentimentAgent()
