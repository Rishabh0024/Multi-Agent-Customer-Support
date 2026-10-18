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
1. "greeting": Pure greetings or salutations (e.g., 'hi', 'hello', 'hey', 'good morning', 'namaste', 'kaise ho').
2. "casual_chat": Pleasantries, gratitude, casual conversational remarks (e.g., 'thanks', 'how are you', 'ok', 'acha', 'theek hai', 'cool'), OR language preferences (e.g., 'can you talk in hindi', 'hindi me baat karo', 'aap mujhe hindi me bata skte hai').
3. "session_query": Questions asking about the current chat session or active ticket (e.g., 'what is my ticket number?', 'mera ticket number kya hai?', 'ticket status?').
4. "escalation_request": Explicit request to talk to a human agent/manager, OR confirming an offer to open a ticket.
5. "complaint": Severe dissatisfaction, anger, scam/fraud allegations, defective product complaints, or legal threats.
6. "rag_query": Legitimate customer support questions or requests about orders, shipping, returns, warranty, billing, account, or company policies.
7. "out_of_domain": Questions or requests completely unrelated to our store/support domain (e.g., coding, general trivia, politics, recipes).

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

        # 1. Ticket / Session status query (e.g. "what is my ticket number?", "mera ticket no kya hai?")
        if any(phrase in lower_msg for phrase in [
            "ticket number", "ticket no", "mera ticket", "kya ticket", "ticket status",
            "active ticket", "my ticket", "ticket banaya", "ticket generate", "ticket details"
        ]):
            intent = "session_query"

        # 2. Language requests (e.g. "can you talk in hindi", "hindi me baat karo", "aap mujhe hindi me bata skte hai")
        elif any(phrase in lower_msg for phrase in [
            "hindi me", "talk in hindi", "speak in hindi", "hindi me bata", "hindi bolo",
            "hindi aati hai", "can you speak hindi", "can you talk to me in hindi", "english me", "talk in english"
        ]):
            intent = "casual_chat"

        # 3. Check if assistant previously offered escalation, and user is affirming it
        elif any(phrase in (history[-1].get("content", "").lower() if history else "") for phrase in [
            "connect you with a human", "connect with a human", "open a support ticket",
            "human specialist", "support ticket for you", "create a ticket", "escalate this issue"
        ]) and (clean_msg in {"yes", "yeah", "yep", "sure", "please", "ok", "okay", "do that", "yes please", "connect me", "open ticket"} or any(w in lower_msg.split() for w in ["yes", "yeah", "please", "connect"])):
            intent = "escalation_request"

        # 4. Pure Greetings (only if message is short greeting, not a full question)
        elif clean_msg in {
            "hi", "hello", "hey", "good morning", "good evening", "good afternoon",
            "namaste", "namaskar", "hola", "greetings", "kaise ho", "kya haal hai"
        } or (len(clean_msg.split()) <= 2 and any(clean_msg.startswith(g) for g in ["hi ", "hello ", "hey "])):
            intent = "greeting"

        # 5. Casual chit-chat / gratitude / pleasantries (Hindi + English)
        elif clean_msg in {
            "thanks", "thank you", "thx", "thank you so much", "thanks a lot", "shukriya", "dhanyawad",
            "how are you", "how are you doing", "who are you", "what can you do", "kya kar sakte ho",
            "ok", "okay", "alright", "got it", "cool", "bye", "goodbye", "see you",
            "acha", "achha", "theek hai", "thik h", "theek h", "sahi hai", "haan", "han"
        }:
            intent = "casual_chat"

        # 6. Explicit human escalation phrases
        elif any(phrase in lower_msg for phrase in [
            "talk to human", "speak to human", "real person", "manager",
            "human representative", "human agent", "escalate to human",
            "connect to agent", "connect me with human", "transfer to human",
            "open a ticket", "create a ticket", "human support", "speak to a person"
        ]):
            intent = "escalation_request"

        # 7. Severe complaints
        elif any(w in lower_msg for w in ["scam", "fraud", "sue you", "worst service", "lawyer", "consumer court", "cheated", "stolen"]):
            intent = "complaint"

        # 8. Obvious Out-of-Domain indicators
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
                        if parsed_intent in ["greeting", "casual_chat", "session_query", "escalation_request", "complaint", "rag_query", "out_of_domain"]:
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
