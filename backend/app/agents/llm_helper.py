from typing import Optional, Dict, Any, List
from app.agents.llm_pool import llm_queue_manager
from app.core.logging import logger

class LLMHelper:
    """Delegates completions to LLMQueueManager with FIFO queueing, rate-pacing, and multi-model rotation."""

    def __init__(self):
        self.queue_manager = llm_queue_manager

    @property
    def client(self) -> bool:
        """Returns True if any active LLM provider is available in the pool."""
        return len(self.queue_manager.pool) > 0

    @property
    def active_model_name(self) -> Optional[str]:
        return self.queue_manager.active_model_name

    @property
    def last_transition(self) -> Optional[str]:
        return self.queue_manager.last_transition

    @property
    def last_pacing_notice(self) -> Optional[str]:
        return self.queue_manager.last_pacing_notice

    @property
    def last_error(self) -> Optional[str]:
        return self.queue_manager.last_error

    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 800,
        response_format: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """Dispatches request via the FIFO Queue Manager with rate-pacing & multi-cloud failover."""
        res, model, transition, pacing = await self.queue_manager.submit(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format
        )
        return res

llm_helper = LLMHelper()
