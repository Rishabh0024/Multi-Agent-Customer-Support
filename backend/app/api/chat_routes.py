from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.db.database import get_db_session
from app.db.models import ChatSession, ChatMessage, Ticket, Feedback, User
from app.schemas.chat import ChatRequest, ChatResponse, DocumentCitation, FeedbackRequest, MessageHistoryItem
from app.memory.session_memory import session_memory
from app.agents.graph import agent_graph
from app.core.logging import logger

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def process_chat_message(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Processes user chat messages through the multi-agent orchestration graph."""
    session_id = payload.session_id.strip()
    user_message = payload.message.strip()

    # 1. Retrieve or create session in PostgreSQL
    stmt = select(ChatSession).where(ChatSession.session_id == session_id)
    result = await db.execute(stmt)
    session_obj = result.scalars().first()

    if not session_obj:
        session_obj = ChatSession(
            session_id=session_id,
            title=f"Chat {session_id[:8]}"
        )
        db.add(session_obj)
        await db.flush()

    # 2. Save user message to PostgreSQL
    user_msg_record = ChatMessage(
        session_id=session_id,
        sender="user",
        content=user_message,
        created_at=datetime.utcnow()
    )
    db.add(user_msg_record)
    await db.flush()

    # 3. Retrieve conversation history from Redis/memory (with DB fallback)
    history = session_memory.get_history(session_id)
    if not history:
        msg_stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        msg_res = await db.execute(msg_stmt)
        db_messages = msg_res.scalars().all()
        # Exclude the current turn user message we just flushed
        for m in db_messages[:-1]:
            history.append({
                "role": "user" if m.sender == "user" else "assistant",
                "content": m.content
            })

    # Check if this session already has an active support ticket
    existing_ticket_stmt = (
        select(Ticket)
        .where(Ticket.session_id == session_id)
        .order_by(Ticket.created_at.desc())
    )
    existing_ticket_res = await db.execute(existing_ticket_stmt)
    existing_ticket = existing_ticket_res.scalars().first()
    existing_ticket_number = existing_ticket.ticket_number if existing_ticket else None

    # 4. Execute Multi-Agent Graph
    agent_output = await agent_graph.execute(
        session_id=session_id,
        user_message=user_message,
        history=history,
        existing_ticket_number=existing_ticket_number
    )

    final_response = agent_output.get("final_response", "")
    sentiment_label = agent_output.get("sentiment_label", "neutral")
    sentiment_score = agent_output.get("sentiment_score", 0.5)
    intent = agent_output.get("intent", "general_inquiry")
    escalation_required = agent_output.get("escalation_required", False)
    ticket_number = agent_output.get("ticket_number") or existing_ticket_number
    confidence_score = agent_output.get("confidence_score", 0.5)
    trajectory = agent_output.get("agent_trajectory", [])
    retrieved_docs = agent_output.get("retrieved_docs", [])

    # Update user message sentiment/intent
    user_msg_record.sentiment = sentiment_label
    user_msg_record.sentiment_score = sentiment_score
    user_msg_record.intent = intent

    # 5. If escalated, persist Ticket in PostgreSQL (or update existing)
    if escalation_required and ticket_number:
        if not existing_ticket:
            new_ticket = Ticket(
                ticket_number=ticket_number,
                session_id=session_id,
                customer_name=payload.user_name or "Anonymous Customer",
                customer_email=payload.user_email,
                issue_summary=agent_output.get("ticket_summary", f"Customer inquiry: {user_message[:100]}"),
                details=f"User Message: {user_message}\nAssigned Priority based on sentiment score: {sentiment_score}",
                priority="urgent" if sentiment_score < 0.25 else ("high" if sentiment_score < 0.35 else "medium"),
                status="escalated",
                sentiment_score=sentiment_score
            )
            db.add(new_ticket)
            session_obj.status = "escalated"
            logger.info(f"Saved escalated Ticket #{ticket_number} to PostgreSQL.")
        else:
            existing_ticket.details += f"\nFollow-up: {user_message}"
            logger.info(f"Appended follow-up to existing Ticket #{existing_ticket.ticket_number} for session {session_id}.")

    # 6. Save assistant response to PostgreSQL
    assistant_msg_record = ChatMessage(
        session_id=session_id,
        sender="assistant",
        content=final_response,
        sentiment=sentiment_label,
        sentiment_score=sentiment_score,
        intent=intent,
        agent_trajectory=trajectory,
        created_at=datetime.utcnow()
    )
    db.add(assistant_msg_record)

    await db.commit()

    # 7. Update sliding window session memory
    session_memory.add_turn(session_id, user_message, final_response)

    # 8. Prepare citations
    citations = [
        DocumentCitation(
            title=doc.get("title", ""),
            category=doc.get("category", "General"),
            score=round(doc.get("score", 0.0), 3)
        )
        for doc in retrieved_docs
    ]

    return ChatResponse(
        session_id=session_id,
        message=final_response,
        sentiment_label=sentiment_label,
        sentiment_score=sentiment_score,
        intent=intent,
        escalation_required=escalation_required,
        ticket_number=ticket_number,
        confidence_score=confidence_score,
        agent_trajectory=trajectory,
        citations=citations,
        model_used=agent_output.get("model_used"),
        model_error=agent_output.get("model_error")
    )

@router.get("/{session_id}/history")
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieves all chat messages for a specific session."""
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    return [
        {
            "id": msg.id,
            "sender": msg.sender,
            "content": msg.content,
            "sentiment": msg.sentiment,
            "sentiment_score": msg.sentiment_score,
            "intent": msg.intent,
            "agent_trajectory": msg.agent_trajectory or [],
            "created_at": msg.created_at.isoformat() if msg.created_at else ""
        }
        for msg in messages
    ]

@router.post("/feedback")
async def submit_feedback(
    payload: FeedbackRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Submits user satisfaction rating for an assistant response."""
    feedback = Feedback(
        session_id=payload.session_id,
        message_id=payload.message_id,
        rating=payload.rating,
        comment=payload.comment
    )
    db.add(feedback)
    await db.commit()
    return {"status": "success", "message": "Feedback recorded successfully"}
