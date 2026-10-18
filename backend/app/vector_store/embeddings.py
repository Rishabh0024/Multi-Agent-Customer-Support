import hashlib
import math
from typing import List
from app.core.config import settings
from app.core.logging import logger

class EmbeddingService:
    def __init__(self):
        self.openai_client = None
        self.has_gemini = False
        self.dimension = 768 if settings.GEMINI_API_KEY else 1536
        self._init_providers()

    def _init_providers(self):
        # 1. Google Gemini Embeddings
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.has_gemini = True
                self.dimension = 768  # models/text-embedding-004 produces 768 dimensions
                logger.info(f"Google Gemini Embeddings initialized with model {settings.GEMINI_EMBEDDING_MODEL} (dim: {self.dimension})")
            except Exception as e:
                logger.warning(f"Could not initialize Google Gemini embeddings: {e}")

        # 2. OpenAI Embeddings (Alternative)
        if not self.has_gemini and settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                self.dimension = 1536
                logger.info(f"OpenAI Embedding client initialized with model {settings.EMBEDDING_MODEL} (dim: {self.dimension})")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI embedding client: {e}")

    async def get_embedding(self, text: str, is_query: bool = False) -> List[float]:
        """Gets embedding vector for a single text string."""
        # 1. Try Gemini
        if self.has_gemini:
            try:
                import google.generativeai as genai
                task_type = "retrieval_query" if is_query else "retrieval_document"
                result = genai.embed_content(
                    model=settings.GEMINI_EMBEDDING_MODEL,
                    content=text,
                    task_type=task_type
                )
                embedding = result.get("embedding", [])
                if embedding:
                    return embedding
            except Exception as e:
                logger.error(f"Error calling Gemini embeddings API: {e}. Falling back...")

        # 2. Try OpenAI
        if self.openai_client:
            try:
                response = await self.openai_client.embeddings.create(
                    input=[text],
                    model=settings.EMBEDDING_MODEL
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"Error calling OpenAI embeddings API: {e}. Falling back...")

        # 3. Fallback deterministic pseudo-embedding
        return self._generate_fallback_vector(text)

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of texts."""
        embeddings = []
        for t in texts:
            emb = await self.get_embedding(t, is_query=False)
            embeddings.append(emb)
        return embeddings

    def _generate_fallback_vector(self, text: str) -> List[float]:
        """Generates a normalized dimension-matched vector based on text token hashing."""
        vector = [0.0] * self.dimension
        words = text.lower().split()
        if not words:
            return vector

        for word in words:
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            val = ((h >> 8) % 1000) / 1000.0 - 0.5
            vector[idx] += val

        # L2 Normalize
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]
        return vector

embedding_service = EmbeddingService()
