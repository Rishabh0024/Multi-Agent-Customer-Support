import json
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.core.logging import logger

class LLMHelper:
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        self.has_llm = False
        self.active_model_name: Optional[str] = None
        self.last_error: Optional[str] = None
        self.last_notice: Optional[str] = None
        self.failed_models: List[str] = []
        self._init_providers()

    def _init_providers(self):
        # 1. Google Gemini (Google AI Studio Free API)
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
                self.has_llm = True
                self.active_model_name = settings.GEMINI_MODEL
                logger.info(f"Google Gemini LLM initialized with model {settings.GEMINI_MODEL}")
            except Exception as e:
                self.last_error = f"Gemini init error: {e}"
                logger.warning(f"Could not initialize Google Gemini client: {e}")

        # 2. OpenAI Alternative
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                self.has_llm = True
                self.active_model_name = settings.LLM_MODEL
                logger.info(f"OpenAI LLM initialized with model {settings.LLM_MODEL}")
            except Exception as e:
                self.last_error = f"OpenAI init error: {e}"
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
        self.last_error = None
        self.failed_models = []

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

                candidate_models = [settings.GEMINI_MODEL, "gemini-flash-latest", "gemini-3.8-flash", "models/gemini-2.5-flash-lite"]
                # Deduplicate preserving order
                unique_models = []
                for m in candidate_models:
                    if m and m not in unique_models:
                        unique_models.append(m)

                for model_name in unique_models:
                    try:
                        model_instance = genai.GenerativeModel(
                            model_name=model_name,
                            generation_config=generation_config
                        )
                        response = await model_instance.generate_content_async(full_prompt)
                        result_text = None
                        try:
                            if hasattr(response, "text") and response.text:
                                result_text = response.text.strip()
                        except Exception:
                            pass
                        if not result_text and hasattr(response, "candidates") and response.candidates:
                            first = response.candidates[0]
                            if hasattr(first, "content") and first.content and hasattr(first.content, "parts"):
                                parts_text = "".join(getattr(p, "text", "") for p in first.content.parts)
                                if parts_text.strip():
                                    result_text = parts_text.strip()

                        if result_text:
                            self.active_model_name = model_name
                            if self.failed_models:
                                self.last_notice = f"Failover: {len(self.failed_models)} model(s) unavailable. Switched to '{model_name}'."
                            else:
                                self.last_notice = None
                            self.last_error = None
                            return result_text
                    except Exception as model_err:
                        err_str = str(model_err)
                        self.failed_models.append(f"{model_name} ({err_str[:60]})")
                        logger.warning(f"Gemini model {model_name} failed: {err_str}. Trying next candidate...")
                        continue

                self.last_error = f"Gemini models failed: {', '.join(self.failed_models)}"
            except Exception as e:
                self.last_error = f"Gemini generation error: {e}"
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
                content = response.choices[0].message.content.strip()
                if content:
                    self.active_model_name = settings.LLM_MODEL
                    if self.failed_models:
                        self.last_notice = f"Failover: Gemini unavailable. Switched to OpenAI '{settings.LLM_MODEL}'."
                    else:
                        self.last_notice = None
                    self.last_error = None
                    return content
            except Exception as e:
                self.failed_models.append(f"OpenAI {settings.LLM_MODEL} ({str(e)[:60]})")
                logger.error(f"OpenAI API call failed: {e}")

        self.active_model_name = None
        self.last_error = f"All LLM models failed: {', '.join(self.failed_models) if self.failed_models else 'No responsive model found'}."
        return None

llm_helper = LLMHelper()
