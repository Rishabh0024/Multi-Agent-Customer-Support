from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class KnowledgeDocCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    category: str = Field(default="General", max_length=100)
    content: str = Field(..., min_length=10)
    metadata: Optional[Dict[str, Any]] = None

class KnowledgeDocResponse(BaseModel):
    id: str
    title: str
    category: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class KnowledgeSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 4
