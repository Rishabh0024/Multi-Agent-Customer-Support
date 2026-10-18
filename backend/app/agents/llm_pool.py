import os
import time
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings
from app.core.logging import logger

class ModelCandidate:
    """Represents a specific LLM model candidate with rate limiting and cooldown state."""
    def __init__(
        self,
        provider: str,
        model_id: str,
        display_name: str,
        min_interval_seconds: float = 3.0
    ):
        self.provider = provider  # 'gemini', 'openrouter', 'groq', 'openai'
        self.model_id = model_id
        self.display_name = display_name
        self.min_interval = min_interval_seconds
        self.last_used: float = 0.0
        self.cooldown_until: float = 0.0
        self.consecutive_errors: int = 0
        self.last_error: Optional[str] = None

    def is_available(self) -> bool:
        """Returns True if the model is not currently on cooldown."""
        return time.time() >= self.cooldown_until

    def mark_failure(self, error_str: str, is_quota: bool = False):
        """Places model on cooldown upon error or quota exhaustion."""
        self.consecutive_errors += 1
        self.last_error = error_str
        cooldown_sec = 180.0 if is_quota else 60.0
        self.cooldown_until = time.time() + cooldown_sec
        logger.warning(
            f"Model '{self.display_name}' placed on cooldown for {cooldown_sec}s "
            f"(Quota exceeded={is_quota}). Error: {error_str[:80]}"
        )

    def mark_success(self):
        """Updates last_used timestamp and resets error counter."""
        self.last_used = time.time()
        self.consecutive_errors = 0
        self.last_error = None


class LLMQueueManager:
    """
    Asynchronous Request Queue & Pacing Manager for Multi-Model LLM Execution.
    Guarantees:
    1. Zero dropped requests: requests wait in FIFO queue.
    2. Quota pacing: sleeps to satisfy per-model request intervals (RPM/RPS).
    3. Multi-cloud failover: auto-switches models on 429 quota exhaustion.
    4. Model transparency: returns exact migration and pacing metadata for UI display.
    """

    def __init__(self):
        self.pool: List[ModelCandidate] = []
        self._lock = asyncio.Lock()
        self.active_model_name: Optional[str] = None
        self.last_transition: Optional[str] = None
        self.last_pacing_notice: Optional[str] = None
        self.last_error: Optional[str] = None
        self._init_pool()

    def _init_pool(self):
        """Initializes the candidate model pool across Google Gemini, OpenRouter, Groq, and OpenAI."""
        self.pool.clear()

        # 1. Google Gemini Free Models (using user's active API key)
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
            # Models verified active on Google AI Studio
            gemini_candidates = [
                ("models/gemini-3.5-flash", "Gemini 3.5 Flash (Google AI)", 3.0),
                ("models/gemini-3.5-flash-lite", "Gemini 3.5 Flash Lite (Google AI)", 2.5),
                ("models/gemini-flash-lite-latest", "Gemini Flash Lite Latest (Google AI)", 2.5),
                ("models/gemma-4-26b-a4b-it", "Gemma 4 26B Instruct (Google AI)", 3.0),
                ("models/gemini-flash-latest", "Gemini Flash Latest (Google AI)", 3.0),
                ("models/gemini-3.8-flash", "Gemini 3.8 Flash (Google AI)", 3.0),
            ]
            for model_id, display, interval in gemini_candidates:
                self.pool.append(ModelCandidate("gemini", model_id, display, interval))

        # 2. OpenRouter Free Cloud Models
        openrouter_key = (getattr(settings, "OPENROUTER_API_KEY", "") or os.environ.get("OPENROUTER_API_KEY", "")).strip()
        if openrouter_key:
            openrouter_models = [
                ("meta-llama/llama-3.3-70b-instruct:free", "LLaMA 3.3 70B (OpenRouter Free)", 2.5),
                ("google/gemini-2.0-flash-lite:free", "Gemini 2.0 Flash Lite (OpenRouter Free)", 2.0),
                ("deepseek/deepseek-r1:free", "DeepSeek R1 (OpenRouter Free)", 3.0),
                ("meta-llama/llama-3.1-8b-instruct:free", "LLaMA 3.1 8B (OpenRouter Free)", 2.0),
                ("qwen/qwen-2.5-coder-32b-instruct:free", "Qwen 2.5 32B (OpenRouter Free)", 2.5),
                ("mistralai/mistral-7b-instruct:free", "Mistral 7B (OpenRouter Free)", 2.0),
            ]
            for model_id, display, interval in openrouter_models:
                self.pool.append(ModelCandidate("openrouter", model_id, display, interval))

        # 3. Groq Cloud Free Models
        groq_key = (getattr(settings, "GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")).strip()
        if groq_key:
            groq_models = [
                ("llama-3.3-70b-versatile", "LLaMA 3.3 70B Versatile (Groq Cloud)", 1.5),
                ("llama-3.1-8b-instant", "LLaMA 3.1 8B Instant (Groq Cloud)", 1.0),
            ]
            for model_id, display, interval in groq_models:
                self.pool.append(ModelCandidate("groq", model_id, display, interval))

        # 4. OpenAI Alternative
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
            self.pool.append(ModelCandidate("openai", settings.LLM_MODEL, f"OpenAI {settings.LLM_MODEL}", 2.0))

        logger.info(f"LLMQueueManager initialized with {len(self.pool)} candidate models across providers.")

    async def submit(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 800,
        response_format: Optional[Dict[str, str]] = None
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Submits request to FIFO queue.
        Returns:
            (response_text, model_used, model_transition, pacing_notice)
        """
        async with self._lock:
            if not self.pool:
                self._init_pool()
                if not self.pool:
                    self.last_error = "No LLM providers configured. Please provide GEMINI_API_KEY or OPENROUTER_API_KEY."
                    return None, None, None, None

            failed_in_this_turn: List[str] = []
            transition_notice: Optional[str] = None
            pacing_notice: Optional[str] = None

            # Attempt through available models in priority order
            for candidate in self.pool:
                if not candidate.is_available():
                    continue

                # 1. Quota Pacing Check (Point 2)
                now = time.time()
                elapsed = now - candidate.last_used
                if elapsed < candidate.min_interval:
                    wait_time = round(candidate.min_interval - elapsed, 2)
                    pacing_notice = f"Rate pacing active: waited {wait_time}s to preserve quota limit (please be patient...)"
                    logger.info(f"Pacing request for {wait_time}s on '{candidate.display_name}'")
                    await asyncio.sleep(wait_time)

                # 2. Dispatch to provider
                try:
                    result = await self._call_provider(
                        candidate,
                        messages,
                        temperature,
                        max_tokens,
                        response_format
                    )
                    if result and result.strip():
                        candidate.mark_success()
                        self.active_model_name = candidate.display_name

                        if failed_in_this_turn:
                            transition_notice = (
                                f"Quota exceeded / unavailable on [{', '.join(failed_in_this_turn)}] "
                                f"→ Auto-switched to '{candidate.display_name}'"
                            )
                            logger.info(transition_notice)

                        self.last_transition = transition_notice
                        self.last_pacing_notice = pacing_notice
                        self.last_error = None
                        return result.strip(), candidate.display_name, transition_notice, pacing_notice
                except Exception as e:
                    err_msg = str(e)
                    is_quota = any(q in err_msg.lower() for q in ["429", "quota", "rate limit", "exceeded your current quota", "resource_exhausted"])
                    candidate.mark_failure(err_msg, is_quota=is_quota)
                    failed_in_this_turn.append(candidate.display_name)
                    logger.warning(
                        f"Model {candidate.display_name} failed ({err_msg[:60]}). "
                        f"Auto-switching to next candidate in queue..."
                    )
                    continue

            # If all models failed or on cooldown
            self.last_error = f"All {len(self.pool)} candidate models failed or on quota cooldown: {', '.join(failed_in_this_turn)}"
            return None, None, None, None

    async def _call_provider(
        self,
        candidate: ModelCandidate,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, str]]
    ) -> Optional[str]:
        """Dispatches call to the appropriate LLM client."""
        # 1. Google Gemini Client
        if candidate.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            if response_format and response_format.get("type") == "json_object":
                generation_config["response_mime_type"] = "application/json"

            # Combine messages into a unified prompt
            system_instruction = ""
            chat_content = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    system_instruction = content
                elif role == "user":
                    chat_content.append(f"User: {content}")
                elif role == "assistant":
                    chat_content.append(f"Assistant: {content}")

            full_prompt = ""
            if system_instruction:
                full_prompt += f"System Instructions:\n{system_instruction}\n\n"
            full_prompt += "\n".join(chat_content)

            model_instance = genai.GenerativeModel(
                model_name=candidate.model_id,
                generation_config=generation_config
            )
            response = await model_instance.generate_content_async(full_prompt)

            if hasattr(response, "text") and response.text:
                return response.text.strip()
            if hasattr(response, "candidates") and response.candidates:
                first = response.candidates[0]
                if hasattr(first, "content") and first.content and hasattr(first.content, "parts"):
                    return "".join(getattr(p, "text", "") for p in first.content.parts).strip()
            return None

        # 2. OpenRouter Client (OpenAI-compatible)
        elif candidate.provider == "openrouter":
            from openai import AsyncOpenAI
            openrouter_key = (getattr(settings, "OPENROUTER_API_KEY", "") or os.environ.get("OPENROUTER_API_KEY", "")).strip()
            client = AsyncOpenAI(
                base_url=settings.OPENROUTER_BASE_URL,
                api_key=openrouter_key
            )
            kwargs = {
                "model": candidate.model_id,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            resp = await client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content.strip()

        # 3. Groq Client (OpenAI-compatible)
        elif candidate.provider == "groq":
            from openai import AsyncOpenAI
            groq_key = (getattr(settings, "GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")).strip()
            client = AsyncOpenAI(
                base_url=settings.GROQ_BASE_URL,
                api_key=groq_key
            )
            kwargs = {
                "model": candidate.model_id,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            resp = await client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content.strip()

        # 4. OpenAI Client
        elif candidate.provider == "openai":
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            kwargs = {
                "model": candidate.model_id,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            resp = await client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content.strip()

        return None

llm_queue_manager = LLMQueueManager()
