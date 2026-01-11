from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App Config
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # LLM Config
    OPENAI_API_KEY: str
    OPENAI_MODEL_NAME: str = "gpt-4-turbo"
    OPENAI_BASE_URL: str = "https://api.apiyi.com/v1"

    # Database / Redis (Optional)
    REDIS_URL: str = "redis://localhost:6379/0"

settings = Settings()