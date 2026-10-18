from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class TicketCreate(BaseModel):
    session_id: Optional[str] = None
    customer_name: Optional[str] = "Anonymous Customer"
    customer_email: Optional[str] = None
    issue_summary: str
    details: Optional[str] = None
    priority: str = "medium"  # low, medium, high, urgent
    sentiment_score: Optional[float] = None

class TicketUpdateStatus(BaseModel):
    status: str = Field(..., pattern="^(open|escalated|in_progress|resolved|closed)$")
    agent_notes: Optional[str] = None

class TicketResponse(BaseModel):
    id: str
    ticket_number: str
    session_id: Optional[str]
    customer_name: str
    customer_email: Optional[str]
    issue_summary: str
    details: Optional[str]
    priority: str
    status: str
    sentiment_score: Optional[float]
    agent_notes: Optional[str]
    created_at: str
    updated_at: str

class TicketStatsResponse(BaseModel):
    total_tickets: int
    open_tickets: int
    escalated_tickets: int
    resolved_tickets: int
    high_priority_tickets: int
