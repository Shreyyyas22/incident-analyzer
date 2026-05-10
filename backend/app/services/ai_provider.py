"""
AI Provider abstraction layer.
Supports Gemini and Groq with a swappable interface.
"""
import json
import structlog
from abc import ABC, abstractmethod
from app.config import settings

logger = structlog.get_logger()


class AIProvider(ABC):
    @abstractmethod
    async def analyze(self, system_prompt: str, user_prompt: str) -> dict:
        """Send a prompt to the AI and return the parsed JSON response."""
        pass

    def _parse_response(self, raw_text: str) -> dict:
        """Extract JSON from AI response text, handling markdown fences."""
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]  # drop opening fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]  # drop closing fence
            text = "\n".join(lines)
        return json.loads(text)


class GeminiProvider(AIProvider):
    async def analyze(self, system_prompt: str, user_prompt: str) -> dict:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=f"{system_prompt}\n\n{user_prompt}",
        )
        logger.info("Gemini response received", length=len(response.text))
        return self._parse_response(response.text)


class GroqProvider(AIProvider):
    async def analyze(self, system_prompt: str, user_prompt: str) -> dict:
        from groq import Groq

        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        raw = response.choices[0].message.content
        logger.info("Groq response received", length=len(raw))
        return self._parse_response(raw)


def get_ai_provider() -> AIProvider:
    """Factory: returns the correct AI provider based on config."""
    provider = settings.AI_PROVIDER.lower()
    if provider == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required when AI_PROVIDER=groq")
        return GroqProvider()
    else:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when AI_PROVIDER=gemini")
        return GeminiProvider()
