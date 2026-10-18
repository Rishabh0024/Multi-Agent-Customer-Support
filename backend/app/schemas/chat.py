from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique conversation session identifier")
    message: str = Field(..., min_length=1, max_length=4000, description="Customer message")
    user_name: Optional[str] = Field(None, description="Optional customer name")
    user_email: Optional[str] = Field(None, description="Optional customer email")

class DocumentCitation(BaseModel):
    title: str
    category: str
    score: float

class ChatResponse(BaseModel):
    session_id: str
    message: str
    sentiment_label: str
    sentiment_score: float
    intent: str
    escalation_required: bool
    ticket_number: Optional[str] = None
    confidence_score: float
    agent_trajectory: List[str]
    citations: List[DocumentCitation] = []
    model_used: Optional[str] = None
    model_transition: Optional[str] = None
    pacing_notice: Optional[str] = None
    model_error: Optional[str] = None


class MessageHistoryItem(BaseModel):
    id: str
    sender: str
    content: str
    sentiment: Optional[str] = None
    intent: Optional[str] = None
    created_at: str

class FeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    rating: int = Field(..., ge=1, le=5, description="1 to 5 rating")
    comment: Optional[str] = None
