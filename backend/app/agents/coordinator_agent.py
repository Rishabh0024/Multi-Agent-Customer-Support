import json
from app.agents.state import AgentState
from app.agents.llm_helper import llm_helper
from app.core.logging import logger

import re

class CoordinatorAgent:
    """Classifies user intent and routes the query through the multi-agent graph with domain awareness."""

    SYSTEM_PROMPT = """You are the Coordinator & Intent Classification Agent of an enterprise customer support platform.
Your task is to analyze the user's message and recent conversation history to accurately classify intent.

OUR SUPPORT DOMAIN (Allowed Core Topics):
- Orders & Tracking (order status, tracking numbers, delivery delays, cancellations within 1 hr)
- Shipping & Logistics (ground, express, overnight delivery times and costs)
- Returns & Refunds (30-day return policy, return eligibility, refund timeframe)
- Warranty & Hardware Repairs (1-year limited warranty, hardware defect RMA claims)
- Billing & Invoices (credit cards, PayPal, Klarna, PDF tax invoices)
- Account & Security (password reset, 2-factor authentication)
- Human Agent Escalation (connecting to customer support leadership or opening a support ticket)

OUT OF DOMAIN (Forbidden Topics):
- Writing code / programming, math problems, general trivia, world history, politics, sports news, cooking recipes, poems, homework help, personal life advice.

POSSIBLE INTENTS:
1. "greeting": Pure greetings or salutations (e.g., 'hi', 'hello', 'hey', 'good morning', 'namaste').
2. "casual_chat": Pleasantries, politeness, gratitude, or conversational banter (e.g., 'thanks', 'thank you', 'how are you', 'who are you', 'ok got it', 'goodbye').
3. "escalation_request": Explicit request to talk to a human agent/manager, OR confirming/accepting an assistant's prior offer to open a support ticket or connect to human support.
4. "complaint": Severe dissatisfaction, anger, scam/fraud allegations, defective product complaints, or legal threats.
5. "rag_query": Legitimate customer support questions or requests about orders, shipping, returns, warranty, billing, account, or company policies.
6. "out_of_domain": Questions or requests completely unrelated to our store/support domain.

Respond ONLY in JSON format:
{"intent": "<one_of_the_above>", "reasoning": "<short explanation>"}
"""

    async def run(self, state: AgentState) -> AgentState:
        trajectory = list(state.get("agent_trajectory", []))
        trajectory.append("CoordinatorAgent")
        user_message = state["user_message"].strip()
        lower_msg = user_message.lower()
        clean_msg = re.sub(r"[^\w\s]", "", lower_msg).strip()
        history = state.get("history", [])

        # Default fallback intent
        intent = "rag_query"

        # 1. Check if assistant previously offered escalation, and user is affirming it
        last_assistant_msg = ""
        for turn in reversed(history):
            if turn.get("role") == "assistant":
                last_assistant_msg = turn.get("content", "").lower()
                break

        offered_escalation = any(phrase in last_assistant_msg for phrase in [
            "connect you with a human", "connect with a human", "open a support ticket",
            "human specialist", "support ticket for you", "create a ticket", "escalate this issue"
        ])

        affirmative_words = {"yes", "yeah", "yep", "sure", "please", "ok", "okay", "do that", "yes please", "connect me", "open ticket"}
        if offered_escalation and (clean_msg in affirmative_words or any(w in lower_msg.split() for w in ["yes", "yeah", "please", "connect"])):
            intent = "escalation_request"

        # 2. Pure Greetings (only if message is short greeting, not a full question)
        elif clean_msg in {"hi", "hello", "hey", "good morning", "good evening", "good afternoon", "namaste", "hola", "greetings"} or (
            len(clean_msg.split()) <= 2 and any(clean_msg.startswith(g) for g in ["hi ", "hello ", "hey "])
        ):
            intent = "greeting"

        # 3. Casual chit-chat / gratitude / pleasantries
        elif clean_msg in {
            "thanks", "thank you", "thx", "thank you so much", "thanks a lot",
            "how are you", "how are you doing", "who are you", "what can you do",
            "ok", "okay", "alright", "got it", "cool", "bye", "goodbye", "see you"
        }:
            intent = "casual_chat"

        # 4. Explicit human escalation phrases
        elif any(phrase in lower_msg for phrase in [
            "talk to human", "speak to human", "real person", "manager",
            "human representative", "human agent", "escalate to human",
            "connect to agent", "connect me with human", "transfer to human",
            "open a ticket", "create a ticket", "human support", "speak to a person"
        ]):
            intent = "escalation_request"

        # 5. Severe complaints
        elif any(w in lower_msg for w in ["scam", "fraud", "sue you", "worst service", "lawyer", "consumer court", "cheated", "stolen"]):
            intent = "complaint"

        # 6. Obvious Out-of-Domain indicators
        elif any(phrase in lower_msg for phrase in [
            "python code", "write a code", "write code", "javascript", "solve this", "math problem",
            "who is the president", "capital of", "who wrote", "weather in", "write a poem", "write an essay",
            "tell me a story", "cooking recipe", "bake a cake"
        ]):
            intent = "out_of_domain"

        else:
            # If LLM available, get refined classification with history context
            if llm_helper.client:
                recent_history = history[-4:]
                messages = [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"Recent Conversation History: {json.dumps(recent_history)}\nCurrent User Message: {user_message}"}
                ]
                res = await llm_helper.generate_chat_completion(messages, response_format={"type": "json_object"})
                if res:
                    try:
                        data = json.loads(res)
                        parsed_intent = data.get("intent", "rag_query")
                        if parsed_intent in ["greeting", "casual_chat", "escalation_request", "complaint", "rag_query", "out_of_domain"]:
                            intent = parsed_intent
                    except Exception as e:
                        logger.warning(f"Error parsing coordinator response: {e}")

        logger.info(f"[CoordinatorAgent] Classified intent: {intent}")
        return {
            **state,
            "intent": intent,
            "agent_trajectory": trajectory
        }

coordinator_agent = CoordinatorAgent()
