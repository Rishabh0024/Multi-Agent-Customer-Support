from typing import Dict, Any, List, Optional
from app.agents.state import AgentState
from app.agents.coordinator_agent import coordinator_agent
from app.agents.sentiment_agent import sentiment_agent
from app.agents.rag_agent import rag_agent
from app.agents.escalation_agent import escalation_agent
from app.agents.response_agent import response_agent
from app.core.logging import logger

# Try initializing LangGraph StateGraph
try:
    from langgraph.graph import StateGraph, END
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False
    logger.warning("langgraph package not available. Using native orchestration fallback.")

class SupportAgentGraph:
    def __init__(self):
        self.compiled_graph = None
        if HAS_LANGGRAPH:
            self._build_langgraph()

    def _build_langgraph(self):
        try:
            workflow = StateGraph(AgentState)

            # Define agent nodes
            workflow.add_node("coordinator", coordinator_agent.run)
            workflow.add_node("sentiment", sentiment_agent.run)
            workflow.add_node("rag", rag_agent.run)
            workflow.add_node("escalation", escalation_agent.run)
            workflow.add_node("formatter", response_agent.run)

            # Entry point
            workflow.set_entry_point("coordinator")
            workflow.add_edge("coordinator", "sentiment")

            # Conditional routing based on user intent
            def route_after_sentiment(state: AgentState) -> str:
                intent = state.get("intent")
                if intent in ["escalation_request", "complaint"]:
                    return "escalation"
                elif intent in ["greeting", "casual_chat", "out_of_domain", "session_query"]:
                    return "formatter"
                return "rag"

            workflow.add_conditional_edges(
                "sentiment",
                route_after_sentiment,
                {
                    "escalation": "escalation",
                    "formatter": "formatter",
                    "rag": "rag"
                }
            )

            # Conditional routing after RAG
            def route_after_rag(state: AgentState) -> str:
                if state.get("escalation_required", False):
                    return "escalation"
                return "formatter"

            workflow.add_conditional_edges(
                "rag",
                route_after_rag,
                {
                    "escalation": "escalation",
                    "formatter": "formatter"
                }
            )

            workflow.add_edge("escalation", "formatter")
            workflow.add_edge("formatter", END)

            self.compiled_graph = workflow.compile()
            logger.info("LangGraph multi-agent StateGraph compiled successfully.")
        except Exception as e:
            logger.error(f"Error compiling LangGraph: {e}. Fallback to manual execution.")
            self.compiled_graph = None

    async def execute(
        self,
        session_id: str,
        user_message: str,
        history: List[Dict[str, str]],
        existing_ticket_number: Optional[str] = None
    ) -> AgentState:
        """Executes the multi-agent graph with the given user message."""
        initial_state: AgentState = {
            "session_id": session_id,
            "user_message": user_message,
            "history": history,
            "intent": "general_inquiry",
            "sentiment_label": "neutral",
            "sentiment_score": 0.5,
            "retrieved_docs": [],
            "raw_answer": "",
            "escalation_required": False,
            "ticket_id": None,
            "ticket_number": existing_ticket_number,
            "ticket_summary": None,
            "final_response": "",
            "agent_trajectory": [],
            "confidence_score": 0.5,
            "existing_ticket_number": existing_ticket_number,
            "model_used": None,
            "model_error": None
        }

        # Use LangGraph if available
        if self.compiled_graph:
            try:
                result = await self.compiled_graph.ainvoke(initial_state)
                return result
            except Exception as e:
                logger.error(f"LangGraph ainvoke error ({e}), executing native graph flow.")

        # Native fallback flow reproducing exact graph edges
        state = await coordinator_agent.run(initial_state)
        state = await sentiment_agent.run(state)

        intent = state.get("intent", "rag_query")
        if intent in ["escalation_request", "complaint"]:
            state = await escalation_agent.run(state)
        elif intent in ["greeting", "casual_chat", "out_of_domain", "session_query"]:
            pass  # Skips RAG and escalation; directly formats response
        else:
            state = await rag_agent.run(state)
            if state.get("escalation_required", False):
                state = await escalation_agent.run(state)

        state = await response_agent.run(state)
        return state

agent_graph = SupportAgentGraph()
