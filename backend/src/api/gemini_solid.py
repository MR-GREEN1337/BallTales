import asyncio
from typing import Any, Optional, Tuple
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Literal

GEMINI_MODELS = [
    "gemini-1.5-flash-8b",
    "gemini-1.5-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-pro",
]


class GeminiSolid:
    def __init__(self):
        # Model hierarchy from fastest/smallest to most capable
        self.model_hierarchy = GEMINI_MODELS

        # Initialize all models
        self.models = {
            model_name: genai.GenerativeModel(model_name)
            for model_name in self.model_hierarchy
        }

    def is_rate_limit_error(self, exception: Exception) -> bool:
        """Check if the exception is a rate limit error"""
        return isinstance(exception, Exception) and "429" in str(exception)

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=lambda x: isinstance(x, Exception) and "429" in str(x),
    )
    async def generate_with_fallback(
        self,
        prompt: str,
        current_model_index: int = 0,
        generation_config: Optional[Any] = None,
        model_name: Optional[Literal[GEMINI_MODELS]] = None,
    ) -> str:
        """
        Generate content with automatic model fallback on rate limit errors.
        Returns the result of the first successful model.
        """
        if current_model_index >= len(self.model_hierarchy):
            raise Exception("All models exhausted")

        try:
            if not model_name:
                model_name = self.model_hierarchy[current_model_index]

            model = self.models[model_name]

            result = await asyncio.to_thread(
                model.generate_content, prompt, generation_config=generation_config
            )
            return result

        except Exception as e:
            if (
                self.is_rate_limit_error(e)
                and current_model_index < len(self.model_hierarchy) - 1
            ):
                # Try next model in hierarchy
                return await self.generate_with_fallback(
                    prompt=prompt,
                    current_model_index=current_model_index + 1,
                    generation_config=generation_config,
                )
            raise
