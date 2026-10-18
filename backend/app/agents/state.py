from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class AgentState(TypedDict):
    session_id: str
    user_message: str
    history: List[Dict[str, str]]
    intent: str
    sentiment_label: str
    sentiment_score: float
    retrieved_docs: List[Dict[str, Any]]
    raw_answer: str
    escalation_required: bool
    ticket_id: Optional[str]
    ticket_number: Optional[str]
    ticket_summary: Optional[str]
    final_response: str
    agent_trajectory: List[str]
    confidence_score: float
    existing_ticket_number: Optional[str]
