from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Telegram AI Assistant"

    # Telegram
    TELEGRAM_BOT_TOKEN: str
    ADMIN_CHAT_ID: Optional[int] = None

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "password"
    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    # Behavior
    MIN_TYPING_DELAY: float = 1.0
    MAX_TYPING_DELAY: float = 3.0
    MESSAGE_CHUNK_SIZE: int = 4000

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
