"""Core configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # App
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    SECRET_KEY: str = "change-me"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/contractiq"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/contractiq"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI providers
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # AI model config
    PRIMARY_MODEL: str = "gpt-4o"
    FALLBACK_MODEL: str = "claude-sonnet-4-5"
    MAX_TOKENS_PER_CHUNK: int = 6000
    CHUNK_OVERLAP: int = 200

    # File upload
    MAX_FILE_SIZE_MB: int = 25
    MAX_PAGES_PER_CONTRACT: int = 150
    ALLOWED_EXTENSIONS: str = "pdf,docx"
    LOCAL_UPLOAD_DIR: str = "./uploads"

    # Clerk
    CLERK_SECRET_KEY: str = ""
    CLERK_JWT_ISSUER: str = ""

    # Storage
    STORAGE_MODE: str = "local"

    @property
    def allowed_extensions_list(self) -> list[str]:
        """Return allowed extensions as a list."""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        """Return max file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
