from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db_session
from app.db.models import Ticket
from app.schemas.ticket import TicketResponse, TicketUpdateStatus, TicketStatsResponse

router = APIRouter(prefix="/api/tickets", tags=["Support Desk Tickets"])

@router.get("", response_model=List[TicketResponse])
async def list_tickets(
    status: Optional[str] = Query(None, description="Filter by status (open, escalated, in_progress, resolved, closed)"),
    priority: Optional[str] = Query(None, description="Filter by priority (low, medium, high, urgent)"),
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session)
):
    """Lists support tickets for the agent dashboard with filtering."""
    stmt = select(Ticket)
    if status:
        stmt = stmt.where(Ticket.status == status)
    if priority:
        stmt = stmt.where(Ticket.priority == priority)

    stmt = stmt.order_by(Ticket.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    tickets = result.scalars().all()

    return [
        TicketResponse(
            id=t.id,
            ticket_number=t.ticket_number,
            session_id=t.session_id,
            customer_name=t.customer_name or "Anonymous",
            customer_email=t.customer_email,
            issue_summary=t.issue_summary,
            details=t.details,
            priority=t.priority,
            status=t.status,
            sentiment_score=t.sentiment_score,
            agent_notes=t.agent_notes,
            created_at=t.created_at.isoformat() if t.created_at else "",
            updated_at=t.updated_at.isoformat() if t.updated_at else ""
        )
        for t in tickets
    ]

@router.get("/stats", response_model=TicketStatsResponse)
async def get_ticket_statistics(db: AsyncSession = Depends(get_db_session)):
    """Computes real-time analytics for the support dashboard."""
    total_res = await db.execute(select(func.count(Ticket.id)))
    total_tickets = total_res.scalar() or 0

    open_res = await db.execute(select(func.count(Ticket.id)).where(Ticket.status.in_(["open", "escalated"])))
    open_tickets = open_res.scalar() or 0

    escalated_res = await db.execute(select(func.count(Ticket.id)).where(Ticket.status == "escalated"))
    escalated_tickets = escalated_res.scalar() or 0

    resolved_res = await db.execute(select(func.count(Ticket.id)).where(Ticket.status.in_(["resolved", "closed"])))
    resolved_tickets = resolved_res.scalar() or 0

    urgent_res = await db.execute(select(func.count(Ticket.id)).where(Ticket.priority.in_(["urgent", "high"])))
    high_priority_tickets = urgent_res.scalar() or 0

    return TicketStatsResponse(
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        escalated_tickets=escalated_tickets,
        resolved_tickets=resolved_tickets,
        high_priority_tickets=high_priority_tickets
    )

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket_detail(
    ticket_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Fetches details for a specific ticket."""
    stmt = select(Ticket).where((Ticket.id == ticket_id) | (Ticket.ticket_number == ticket_id))
    result = await db.execute(stmt)
    ticket = result.scalars().first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        session_id=ticket.session_id,
        customer_name=ticket.customer_name or "Anonymous",
        customer_email=ticket.customer_email,
        issue_summary=ticket.issue_summary,
        details=ticket.details,
        priority=ticket.priority,
        status=ticket.status,
        sentiment_score=ticket.sentiment_score,
        agent_notes=ticket.agent_notes,
        created_at=ticket.created_at.isoformat() if ticket.created_at else "",
        updated_at=ticket.updated_at.isoformat() if ticket.updated_at else ""
    )

@router.patch("/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: str,
    payload: TicketUpdateStatus,
    db: AsyncSession = Depends(get_db_session)
):
    """Updates ticket status and adds human agent notes."""
    stmt = select(Ticket).where((Ticket.id == ticket_id) | (Ticket.ticket_number == ticket_id))
    result = await db.execute(stmt)
    ticket = result.scalars().first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = payload.status
    if payload.agent_notes:
        ticket.agent_notes = payload.agent_notes

    if payload.status in ["resolved", "closed"]:
        ticket.resolved_at = datetime.utcnow()

    await db.commit()
    return {"status": "success", "ticket_number": ticket.ticket_number, "new_status": ticket.status}
