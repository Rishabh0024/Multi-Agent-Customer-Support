from typing import List, Dict, Any
from app.core.config import settings
from app.memory.redis_client import redis_manager

class SessionMemoryManager:
    def __init__(self, max_turns: int = settings.MAX_HISTORY_TURNS):
        self.max_turns = max_turns

    def _get_key(self, session_id: str) -> str:
        return f"session_history:{session_id}"

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Returns the sliding window conversation history for a session."""
        key = self._get_key(session_id)
        history = redis_manager.get_json(key)
        if isinstance(history, list):
            return history
        return []

    def add_turn(self, session_id: str, user_message: str, assistant_message: str):
        """Appends a new turn and maintains sliding window."""
        key = self._get_key(session_id)
        history = self.get_history(session_id)

        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": assistant_message})

        # Keep only the last max_turns * 2 messages (e.g. 8 turns = 16 messages)
        max_messages = self.max_turns * 2
        if len(history) > max_messages:
            history = history[-max_messages:]

        redis_manager.set_json(key, history, expire_seconds=86400 * 2)

    def clear_history(self, session_id: str):
        """Clears memory for a session."""
        key = self._get_key(session_id)
        redis_manager.delete(key)

session_memory = SessionMemoryManager()
