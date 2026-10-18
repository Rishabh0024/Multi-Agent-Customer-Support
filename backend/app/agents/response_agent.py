from app.agents.state import AgentState
from app.agents.llm_helper import llm_helper
from app.core.logging import logger

class ResponseAgent:
    """Formats the final reply, applying tone adaptation, empathy, and escalation notices."""

    SYSTEM_PROMPT = """You are the Senior Response and Persona Agent for an enterprise customer support platform.
Your job is to craft the final response to the customer based on:
1. The raw answer retrieved by the RAG agent.
2. The customer's emotional state (Positive, Neutral, Frustrated, Angry).
3. Whether an escalation ticket was opened.

Formatting Rules:
- If the customer is Frustrated or Angry: Begin with genuine empathy and apology for the inconvenience. Avoid sounding robotic.
- If an escalation ticket was opened: Clearly state the Ticket Number and assure them our human specialist team is notified.
- Maintain a helpful, respectful, and crystal-clear tone.
- Use markdown formatting with bullet points where appropriate for readability.
"""

    async def run(self, state: AgentState) -> AgentState:
        trajectory = list(state.get("agent_trajectory", []))
        trajectory.append("ResponseAgent")

        raw_answer = state.get("raw_answer", "")
        sentiment_label = state.get("sentiment_label", "neutral")
        escalation_required = state.get("escalation_required", False)
        ticket_number = state.get("ticket_number")

        final_response = raw_answer

        # If LLM available, use it for empathetic polishing
        if llm_helper.client:
            prompt_content = f"""
Customer Sentiment: {sentiment_label}
Escalation Status: {'Yes, Ticket #' + ticket_number if escalation_required and ticket_number else 'No'}
Raw Answer: {raw_answer}
User Message: {state['user_message']}

Generate the polished final customer response:
"""
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt_content}
            ]
            res = await llm_helper.generate_chat_completion(messages)
            if res and res.strip():
                final_response = res.strip()

        # Deterministic fallback formatting if LLM was unavailable, failed, or rate-limited
        if not final_response:
            prefix = ""
            if sentiment_label in ["angry", "frustrated"]:
                prefix = "I truly understand your frustration and apologize for the inconvenience this has caused you. "
            
            body = raw_answer if raw_answer else "I have escalated this issue directly to our customer support leadership."
            
            suffix = ""
            if escalation_required and ticket_number:
                suffix = f"\n\n---\n📋 **Support Ticket Created: #{ticket_number}**\nOur human support specialists have been notified with the highest priority and will review this conversation to assist you further."

            final_response = f"{prefix}{body}{suffix}".strip()

        logger.info(f"[ResponseAgent] Final response generated. Trajectory: {' -> '.join(trajectory)}")
        return {
            **state,
            "final_response": final_response,
            "agent_trajectory": trajectory
        }

response_agent = ResponseAgent()
