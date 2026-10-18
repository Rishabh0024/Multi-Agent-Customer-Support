from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.database import get_db_session
from app.db.models import KnowledgeDoc
from app.schemas.knowledge import KnowledgeDocCreate, KnowledgeDocResponse, KnowledgeSearchRequest
from app.vector_store.qdrant_client import qdrant_store
from app.core.logging import logger

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])

@router.get("/list", response_model=List[KnowledgeDocResponse])
async def list_knowledge_documents(db: AsyncSession = Depends(get_db_session)):
    """Retrieves all indexed knowledge documents."""
    stmt = select(KnowledgeDoc).where(KnowledgeDoc.is_active == True).order_by(KnowledgeDoc.created_at.desc())
    result = await db.execute(stmt)
    docs = result.scalars().all()

    return [
        KnowledgeDocResponse(
            id=d.id,
            title=d.title,
            category=d.category,
            content=d.content,
            metadata=d.metadata_info or {}
        )
        for d in docs
    ]

@router.post("/index", response_model=KnowledgeDocResponse)
async def index_knowledge_document(
    payload: KnowledgeDocCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Embeds and indexes a new document into Qdrant and persists in PostgreSQL."""
    # 1. Upsert into Qdrant
    qdrant_doc_id = await qdrant_store.add_document(
        title=payload.title,
        content=payload.content,
        category=payload.category,
        metadata=payload.metadata
    )

    # 2. Persist in PostgreSQL
    doc = KnowledgeDoc(
        title=payload.title,
        category=payload.category,
        content=payload.content,
        embedding_id=qdrant_doc_id,
        metadata_info=payload.metadata or {}
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    logger.info(f"Indexed document '{payload.title}' with Qdrant ID {qdrant_doc_id}")
    return KnowledgeDocResponse(
        id=doc.id,
        title=doc.title,
        category=doc.category,
        content=doc.content,
        metadata=doc.metadata_info
    )

@router.delete("/{doc_id}")
async def delete_knowledge_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Deletes a document from both PostgreSQL and Qdrant."""
    stmt = select(KnowledgeDoc).where(KnowledgeDoc.id == doc_id)
    result = await db.execute(stmt)
    doc = result.scalars().first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from Qdrant if embedding_id exists
    if doc.embedding_id:
        qdrant_store.delete_document(doc.embedding_id)

    await db.delete(doc)
    await db.commit()
    return {"status": "success", "message": f"Document '{doc.title}' deleted successfully"}

@router.post("/search")
async def search_knowledge(payload: KnowledgeSearchRequest):
    """Tests semantic vector search against Qdrant."""
    results = await qdrant_store.search_similar(payload.query, limit=payload.limit or 4)
    return {"query": payload.query, "results": results}

@router.post("/restore-defaults")
async def restore_default_knowledge_documents(db: AsyncSession = Depends(get_db_session)):
    """Restores any missing default knowledge base documents into PostgreSQL and Qdrant."""
    from app.services.knowledge_ingestion import seed_knowledge_base
    await seed_knowledge_base(db)
    return {"status": "success", "message": "Default enterprise knowledge documents verified and restored."}
