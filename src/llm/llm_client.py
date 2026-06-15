import httpx
from src.config.settings import settings
from src.utils.logger import default_logger as logger

class LLMClient:
    def __init__(self):
        self._api_key = settings.llm_api_key
        self._model = settings.llm_model
        self._base_url = settings.llm_base_url
        self._max_tokens = settings.llm_max_tokens
        self._temperature = settings.llm_temperature
        self._frequency_penalty = settings.llm_frequency_penalty
        self._presence_penalty = settings.llm_presence_penalty
        self._top_p = settings.llm_top_p
        self._timeout = settings.llm_timeout
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def generate_answer(self, messages: list[dict]) -> str:
        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
            "frequency_penalty": self._frequency_penalty,
            "presence_penalty": self._presence_penalty,
            "top_p": self._top_p,
        }
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=self._headers,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise
        data = response.json()
        return data["choices"][0]["message"]["content"]
    