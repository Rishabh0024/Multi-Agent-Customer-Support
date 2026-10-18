import json
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.core.logging import logger

class LLMHelper:
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        self.has_llm = False
        self._init_providers()

    def _init_providers(self):
        # 1. Google Gemini (Google AI Studio Free API)
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
                self.has_llm = True
                logger.info(f"Google Gemini LLM initialized with model {settings.GEMINI_MODEL}")
            except Exception as e:
                logger.warning(f"Could not initialize Google Gemini client: {e}")

        # 2. OpenAI Alternative
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                self.has_llm = True
                logger.info(f"OpenAI LLM initialized with model {settings.LLM_MODEL}")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")

    @property
    def client(self):
        """Returns True if any active LLM provider is available."""
        return self.gemini_model or self.openai_client

    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 800,
        response_format: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """Calls Google Gemini or OpenAI Chat Completion."""
        # 1. Prefer Gemini if configured
        if self.gemini_model:
            try:
                import google.generativeai as genai
                generation_config = {
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
                if response_format and response_format.get("type") == "json_object":
                    generation_config["response_mime_type"] = "application/json"

                # Combine messages into a unified Gemini prompt
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
                    model_name=settings.GEMINI_MODEL,
                    generation_config=generation_config
                )
                response = await model_instance.generate_content_async(full_prompt)
                return response.text.strip()
            except Exception as e:
                logger.error(f"Google Gemini generation failed: {e}. Trying fallback...")

        # 2. OpenAI Fallback
        if self.openai_client:
            try:
                kwargs = {
                    "model": settings.LLM_MODEL,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                if response_format:
                    kwargs["response_format"] = response_format

                response = await self.openai_client.chat.completions.create(**kwargs)
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}")

        return None

llm_helper = LLMHelper()
