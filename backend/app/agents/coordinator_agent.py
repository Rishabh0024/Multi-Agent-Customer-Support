import json
from app.agents.state import AgentState
from app.agents.llm_helper import llm_helper
from app.core.logging import logger

class CoordinatorAgent:
    """Classifies user intent and routes the query through the multi-agent graph."""

    SYSTEM_PROMPT = """You are the Coordinator Agent of an enterprise customer support platform.
Your task is to analyze the user's message and recent conversation history to classify the intent.

Possible intents:
1. "greeting": Casual greetings (e.g., 'hello', 'hi', 'good morning').
2. "escalation_request": Explicit request to speak to a human representative or manager.
3. "complaint": Expression of severe dissatisfaction, bad experience, broken item, or legal threat.
4. "rag_query": Questions asking about policies, products, shipping, returns, warranty, troubleshooting.
5. "general_inquiry": General conversational questions or clarifications.

Respond ONLY in JSON format:
{"intent": "<intent_name>", "reasoning": "<short explanation>"}
"""

    async def run(self, state: AgentState) -> AgentState:
        trajectory = list(state.get("agent_trajectory", []))
        trajectory.append("CoordinatorAgent")
        user_message = state["user_message"].strip()
        lower_msg = user_message.lower()

        # Rule-based fast heuristics
        intent = "rag_query"

        # 1. Greetings first
        greeting_words = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon", "namaste", "help"]
        if lower_msg in greeting_words or lower_msg.rstrip("!?.") in greeting_words:
            intent = "greeting"
        # 2. Explicit human escalation phrases
        elif any(phrase in lower_msg for phrase in [
            "talk to human", "speak to human", "real person", "manager",
            "human representative", "human agent", "escalate to human",
            "connect to agent", "connect me with human", "transfer to human"
        ]):
            intent = "escalation_request"
        # 3. Severe complaints
        elif any(w in lower_msg for w in ["scam", "fraud", "sue you", "worst service", "lawyer", "consumer court"]):
            intent = "complaint"
        else:
            # If LLM available, get refined classification
            if llm_helper.client:
                messages = [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"User Message: {user_message}"}
                ]
                res = await llm_helper.generate_chat_completion(messages, response_format={"type": "json_object"})
                if res:
                    try:
                        data = json.loads(res)
                        intent = data.get("intent", "rag_query")
                    except Exception as e:
                        logger.warning(f"Error parsing coordinator response: {e}")

        logger.info(f"[CoordinatorAgent] Classified intent: {intent}")
        return {
            **state,
            "intent": intent,
            "agent_trajectory": trajectory
        }

coordinator_agent = CoordinatorAgent()
