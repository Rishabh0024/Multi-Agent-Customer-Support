from app.agents.state import AgentState
from app.agents.llm_helper import llm_helper
from app.core.logging import logger

class ResponseAgent:
    """Formats the final customer response, handling persona, empathy, domain boundaries, and escalation notices."""

    SYSTEM_PROMPT = """You are the Senior Response and Persona Agent for an enterprise customer support platform.
Your job is to deliver the final response to the customer.

Guidelines:
1. Warm, professional, and helpful tone. Avoid robotic scripting.
2. If the user sent a greeting ('greeting'): Greet them warmly and ask how you can help with orders, shipping, returns, warranty, or account inquiries.
3. If the user sent pleasantries ('casual_chat'): Respond politely and let them know you're here if they need further assistance.
4. If the topic is out of domain ('out_of_domain'): Politely decline and clarify that you are specialized in customer support for our store (orders, shipping, returns, warranty, billing, account).
5. If the customer is Frustrated or Angry: Express genuine empathy and apology for the inconvenience.
6. If an escalation ticket was opened: Clearly display the Ticket Number and reassure them that our human support leadership is reviewing it.
7. If a RAG answer is provided: Deliver it clearly with markdown formatting.
"""

    async def run(self, state: AgentState) -> AgentState:
        trajectory = list(state.get("agent_trajectory", []))
        trajectory.append("ResponseAgent")

        intent = state.get("intent", "rag_query")
        raw_answer = state.get("raw_answer", "")
        sentiment_label = state.get("sentiment_label", "neutral")
        escalation_required = state.get("escalation_required", False)
        ticket_number = state.get("ticket_number")
        user_message = state["user_message"]
        history = state.get("history", [])

        final_response = ""

        # 1. Greetings
        if intent == "greeting":
            if history:
                final_response = "Hello again! How can I continue assisting you with your support inquiry today?"
            else:
                final_response = "Hello! Welcome to Customer Support. I'm here to assist you with orders, returns, warranty, shipping, and account inquiries. How can I help you today?"

        # 2. Casual chit-chat / gratitude
        elif intent == "casual_chat":
            lower_msg = user_message.lower()
            if any(w in lower_msg for w in ["thank", "thx"]):
                final_response = "You're very welcome! Please let me know if there's anything else I can assist you with regarding your order, warranty, or account."
            elif any(w in lower_msg for w in ["how are you", "how are you doing"]):
                final_response = "I'm doing well, thank you for asking! How can I help you today with your orders, products, or account?"
            elif any(w in lower_msg for w in ["who are you", "what can you do"]):
                final_response = "I am your AI Customer Support Assistant! I can help you check policies, track shipments, guide you through returns and warranty claims, or connect you with human specialists."
            else:
                final_response = "Have a great day! Don't hesitate to reach back out if you need any assistance with our services."

        # 3. Out of domain questions
        elif intent == "out_of_domain":
            final_response = (
                "I am dedicated specifically to customer support for our store (assisting with orders, shipping, returns, warranty, billing, and account help). "
                "I'm unable to assist with topics outside this domain. Please let me know if there's anything related to our store or your orders I can help with!"
            )

        # 4. Human Escalation Ticket Created
        elif escalation_required and ticket_number:
            prefix = ""
            if sentiment_label in ["angry", "frustrated"]:
                prefix = "I truly apologize for the frustration and trouble this issue has caused you. "
            final_response = (
                f"{prefix}I have escalated your request directly to our customer support leadership and specialist team.\n\n"
                f"---\n"
                f"📋 **Support Ticket Created: #{ticket_number}**\n"
                f"Our human support specialists have been notified with the highest priority and will review this conversation to assist you promptly."
            )

        # 5. Support Query / RAG Answer
        else:
            final_response = raw_answer

        # If LLM available, use it for empathetic polishing when appropriate
        if llm_helper.client and (sentiment_label in ["angry", "frustrated"] and not ticket_number):
            prompt_content = f"""
Customer Sentiment: {sentiment_label}
Raw Answer: {final_response}
User Message: {user_message}

Refine the customer response with genuine empathy and professional tone:
"""
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt_content}
            ]
            res = await llm_helper.generate_chat_completion(messages)
            if res and res.strip():
                final_response = res.strip()

        # Fallback safeguard
        if not final_response:
            final_response = "How may I assist you with your orders, returns, warranty, or account today?"

        logger.info(f"[ResponseAgent] Final response generated. Trajectory: {' -> '.join(trajectory)}")
        return {
            **state,
            "final_response": final_response,
            "agent_trajectory": trajectory
        }

response_agent = ResponseAgent()
