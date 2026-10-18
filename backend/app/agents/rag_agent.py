import json
from typing import List, Dict, Any
from app.agents.state import AgentState
from app.agents.llm_helper import llm_helper
from app.vector_store.qdrant_client import qdrant_store
from app.core.logging import logger

class RAGAgent:
    """Retrieval-Augmented Generation agent querying knowledge base in Qdrant."""

    SYSTEM_PROMPT = """You are the Knowledge & RAG Retrieval Agent for Customer Support.
Answer the user's question accurately using ONLY the provided knowledge base context snippets.
Guidelines:
1. Ground every statement in the retrieved context.
2. If the context does not contain the answer, politely state that our official documentation does not cover this and offer to connect them with a human specialist.
3. Be clear, concise, and professional.
4. Mention the document title as source citation where applicable.
"""

    async def run(self, state: AgentState) -> AgentState:
        trajectory = list(state.get("agent_trajectory", []))
        trajectory.append("RAGAgent")
        user_message = state["user_message"]

        # Search Qdrant vector store
        docs = await qdrant_store.search_similar(user_message, limit=3)
        logger.info(f"[RAGAgent] Retrieved {len(docs)} documents from Qdrant.")

        raw_answer = ""
        confidence_score = 0.5

        if docs:
            confidence_score = max([d.get("score", 0.5) for d in docs])
            context_text = "\n\n".join([
                f"### Source: {d['title']} ({d['category']})\n{d['content']}"
                for d in docs
            ])

            if llm_helper.client:
                messages = [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"Context:\n{context_text}\n\nUser Question:\n{user_message}"}
                ]
                res = await llm_helper.generate_chat_completion(messages)
                if res:
                    raw_answer = res.strip()
            else:
                # Deterministic synthesis if LLM offline
                top_doc = docs[0]
                raw_answer = (
                    f"According to our **{top_doc['title']}** ({top_doc['category']}):\n\n"
                    f"{top_doc['content'][:450]}...\n\n"
                    f"*Source: {top_doc['title']}*"
                )
        else:
            confidence_score = 0.2
            if state.get("intent") == "greeting":
                raw_answer = "Hello! I am your AI Customer Support Assistant. How can I assist you with your orders, returns, warranty, or account today?"
            else:
                raw_answer = "I searched our knowledge base, but I couldn't find specific documentation directly matching your query. Would you like me to connect you with a human support specialist or open a support ticket for this?"

        return {
            **state,
            "retrieved_docs": docs,
            "raw_answer": raw_answer,
            "confidence_score": round(confidence_score, 2),
            "agent_trajectory": trajectory
        }

rag_agent = RAGAgent()
