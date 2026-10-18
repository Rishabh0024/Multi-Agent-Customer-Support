import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient, models
from app.core.config import settings
from app.core.logging import logger
from app.vector_store.embeddings import embedding_service

class QdrantStore:
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.dimension = embedding_service.dimension
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            if settings.QDRANT_URL and not settings.QDRANT_URL.startswith("memory"):
                self.client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                    timeout=5.0
                )
                # Test connection
                self.client.get_collections()
                logger.info(f"Connected to Qdrant server at {settings.QDRANT_URL}")
            else:
                raise ConnectionError("Qdrant URL set to memory")
        except Exception as e:
            if settings.QDRANT_IN_MEMORY_FALLBACK:
                logger.warning(f"Could not connect to Qdrant at {settings.QDRANT_URL} ({e}). Initializing in-memory Qdrant client.")
                self.client = QdrantClient(":memory:")
            else:
                raise e

        self._ensure_collection()

    def _ensure_collection(self):
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.dimension,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection '{self.collection_name}' with dimension {self.dimension}.")
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection: {e}")

    async def add_document(self, title: str, content: str, category: str = "General", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Embeds and upserts a document into Qdrant."""
        doc_id = str(uuid.uuid4())
        vector = await embedding_service.get_embedding(f"{title}\n{content}")

        payload = {
            "title": title,
            "content": content,
            "category": category,
            "metadata": metadata or {}
        }

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )
        return doc_id

    async def search_similar(self, query: str, limit: int = 4, score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Searches top similar documents for a user query."""
        try:
            query_vector = await embedding_service.get_embedding(query, is_query=True)
            kwargs = {
                "collection_name": self.collection_name,
                "limit": limit
            }
            if score_threshold is not None:
                kwargs["score_threshold"] = score_threshold

            if hasattr(self.client, "query_points"):
                response = self.client.query_points(query=query_vector, **kwargs)
                search_result = response.points
            elif hasattr(self.client, "search"):
                search_result = self.client.search(query_vector=query_vector, **kwargs)
            else:
                search_result = []

            results = []
            for hit in search_result:
                results.append({
                    "id": str(hit.id),
                    "score": float(hit.score),
                    "title": hit.payload.get("title", ""),
                    "content": hit.payload.get("content", ""),
                    "category": hit.payload.get("category", ""),
                    "metadata": hit.payload.get("metadata", {})
                })
            return results
        except Exception as e:
            logger.error(f"Error searching Qdrant vector store: {e}")
            return []

    def get_all_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Returns indexed points for admin dashboard."""
        try:
            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            return [
                {
                    "id": str(p.id),
                    "title": p.payload.get("title", ""),
                    "content": p.payload.get("content", ""),
                    "category": p.payload.get("category", ""),
                    "metadata": p.payload.get("metadata", {})
                }
                for p in points
            ]
        except Exception as e:
            logger.error(f"Error fetching points from Qdrant: {e}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        """Deletes point by ID."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[doc_id])
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting doc {doc_id} from Qdrant: {e}")
            return False

qdrant_store = QdrantStore()
