from __future__ import annotations
import httpx
from src.config.settings import settings

class LLMClient:
    def __init__(self):
      
        self._api_key = settings.llm_api_key
        self._model = settings.llm_model
        self._base_url = settings.llm_base_url
        self._max_tokens = settings.llm_max_tokens
        self._temperature = settings.llm_temperature
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        self._timeout = 60.0

    def generate_answer(self, messages: list[dict]) -> str:
        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
        }
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]