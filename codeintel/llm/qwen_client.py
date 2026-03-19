"""LLM wrapper for Qwen 2.5 Coder (or local fallback)."""

from __future__ import annotations

from typing import Optional

from codeintel.utils.logger import get_logger

logger = get_logger(__name__)


class QwenClient:
    def __init__(self, model: str = "qwen-2.5-coder", endpoint: Optional[str] = None):
        self.model = model
        self.endpoint = endpoint

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Produce text for the prompt.

        NOTE: In this prototype, this method is a stub that returns the prompt.
        Connect to a real LLM (e.g., Qwen hosted API) to get useful responses.
        """
        logger.info("LLM generate called (stub). Returning prompt as response.")
        return prompt
