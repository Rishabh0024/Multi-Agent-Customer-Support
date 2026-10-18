import json
from typing import List, Dict, Any
from app.agents.state import AgentState
from app.agents.llm_helper import llm_helper
from app.vector_store.qdrant_client import qdrant_store
from app.core.logging import logger

class RAGAgent:
    """Retrieval-Augmented Generation agent querying knowledge base in Qdrant with session memory."""

    SYSTEM_PROMPT = """You are the Knowledge & Support Retrieval Agent for an enterprise customer support platform.
Your objective is to provide an accurate, helpful, and natural answer grounded strictly in our official knowledge base documentation and recent conversation history.

Rules:
1. Ground your answer in the provided Documentation Context.
2. Maintain natural continuity with the Conversation History (e.g., if user asks follow-up questions about a previously mentioned policy, order, or product).
3. If the documentation context DOES NOT contain the answer or does not fully cover the user's specific request:
   - State clearly that our official knowledge base does not contain this specific information.
   - Do NOT invent or hallucinate policies.
   - Offer to connect them with a human customer support specialist or open a support ticket.
4. Keep the response polite, clear, and easy to read using markdown bullet points for conditions or steps.
5. Mention the source document title at the end.
"""

    async def run(self, state: AgentState) -> AgentState:
        trajectory = list(state.get("agent_trajectory", []))
        trajectory.append("RAGAgent")
        user_message = state["user_message"].strip()
        history = state.get("history", [])

        # Formulate search query: if message is short (e.g. "how much does it cost?"), use previous turn for context
        search_query = user_message
        if len(user_message.split()) < 5 and history:
            last_user_turn = ""
            for turn in reversed(history):
                if turn.get("role") == "user":
                    last_user_turn = turn.get("content", "")
                    break
            if last_user_turn:
                search_query = f"{last_user_turn} {user_message}"

        # Search Qdrant vector store
        docs = await qdrant_store.search_similar(search_query, limit=3)
        logger.info(f"[RAGAgent] Retrieved {len(docs)} documents from Qdrant for query: '{search_query}'")

        raw_answer = ""
        confidence_score = 0.5
        top_score = docs[0].get("score", 0.0) if docs else 0.0

        # Check if the retrieved documents are relevant
        # Cosine similarity in Qdrant: if >= 0.35, it's considered a relevant match
        if docs and top_score >= 0.35:
            confidence_score = top_score
            context_text = "\n\n".join([
                f"### Document: {d['title']} (Category: {d.get('category', 'Support')})\n{d['content']}"
                for d in docs
            ])

            if llm_helper.client:
                # Include conversation history for multi-turn understanding
                history_snippets = history[-6:]
                user_prompt = f"Documentation Context:\n{context_text}\n\n"
                if history_snippets:
                    user_prompt += f"Recent Conversation History:\n{json.dumps(history_snippets, indent=2)}\n\n"
                user_prompt += f"Current User Question:\n{user_message}"

                messages = [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
                res = await llm_helper.generate_chat_completion(messages)
                if res and res.strip():
                    raw_answer = res.strip()

            # Deterministic synthesis if LLM is offline or rate-limited
            if not raw_answer:
                top_doc = docs[0]
                raw_answer = (
                    f"Based on our official **{top_doc['title']}**:\n\n"
                    f"{top_doc['content']}\n\n"
                    f"*Source: {top_doc['title']} ({top_doc.get('category', 'Support')})*"
                )
        elif docs:
            # Low similarity match or partially relevant
            top_doc = docs[0]
            confidence_score = 0.30
            raw_answer = (
                f"I found some related information in our documentation under **{top_doc['title']}**, but it may not fully address your specific request:\n\n"
                f"{top_doc['content'][:350]}...\n\n"
                f"Would you like me to connect you with a human support specialist or open a support ticket for personalized assistance?"
            )
        else:
            confidence_score = 0.20
            raw_answer = (
                "I searched our official knowledge base, but I couldn't find specific documentation directly answering your inquiry.\n\n"
                "Since this requires specialized assistance, I would be glad to open a support ticket and connect you with a human customer support specialist. Would you like me to open a support ticket for you?"
            )

        return {
            **state,
            "retrieved_docs": docs,
            "raw_answer": raw_answer,
            "confidence_score": round(confidence_score, 2),
            "agent_trajectory": trajectory
        }

rag_agent = RAGAgent()
