import random
import string
import uuid
from datetime import datetime
from app.agents.state import AgentState
from app.core.logging import logger

class EscalationAgent:
    """Handles ticket creation and priority determination when human intervention is needed."""

    def _generate_ticket_number(self) -> str:
        random_suffix = "".join(random.choices(string.digits, k=5))
        return f"TICK-{random_suffix}"

    async def run(self, state: AgentState) -> AgentState:
        trajectory = list(state.get("agent_trajectory", []))
        trajectory.append("EscalationAgent")

        if not state.get("escalation_required", False):
            return {
                **state,
                "agent_trajectory": trajectory
            }

        user_message = state.get("user_message", "")
        sentiment_score = state.get("sentiment_score", 0.5)

        existing_ticket = state.get("existing_ticket_number")
        if existing_ticket:
            ticket_number = existing_ticket
            summary = f"Customer follow-up on existing ticket: {user_message[:100]}"
            logger.info(f"[EscalationAgent] Reusing existing Ticket #{ticket_number} for session {state.get('session_id')}")
        else:
            ticket_number = self._generate_ticket_number()
            summary = f"Customer inquiry requiring human attention: {user_message[:100]}"
            logger.info(f"[EscalationAgent] Escalated to new Ticket #{ticket_number}")

        # Determine priority
        if sentiment_score <= 0.20 or any(w in user_message.lower() for w in ["fraud", "sue", "legal", "stolen", "lost package"]):
            priority = "urgent"
        elif sentiment_score <= 0.35:
            priority = "high"
        else:
            priority = "medium"

        logger.info(f"[EscalationAgent] Escalated to Ticket {ticket_number} (Priority: {priority})")

        return {
            **state,
            "ticket_number": ticket_number,
            "ticket_summary": summary,
            "ticket_id": str(uuid.uuid4()),
            "agent_trajectory": trajectory
        }

escalation_agent = EscalationAgent()
