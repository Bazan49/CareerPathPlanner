from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM 
    llm_api_key: str
    llm_model: str = "mistral-small-latest"
    llm_base_url: str = "https://api.mistral.ai/v1"
    
    # Parámetros de generación (con valores por defecto fijos)
    llm_max_tokens: int = 3000          
    llm_temperature: float = 0.1
    llm_frequency_penalty: float = 0.5
    llm_presence_penalty: float = 0.3
    llm_top_p: float = 0.95
    llm_timeout: float = 60.0

    class Config:
        env_file = ".env"

settings = Settings()