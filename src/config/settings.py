from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM
    llm_api_key: str
    llm_model: str = "mistral-small-latest"
    llm_base_url: str = "https://api.mistral.ai/v1"
    llm_max_tokens: int = 300
    llm_temperature: float = 0.1

    class Config:
        env_file = ".env"

# Instancia global (singleton) para usar en toda la app
settings = Settings()