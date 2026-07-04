"""Central configuration. Every provider choice and API key lives here,
driven by environment variables (see .env.example at repo root)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Provider selection — each one is swappable behind an interface.
    embedding_provider: str = "fashionclip"  # fashionclip | stub
    vibe_provider: str = "gemini"  # gemini | stub
    product_provider: str = "mock"  # mock | serpapi (Day 4)
    vector_store: str = "pgvector"  # pgvector | memory

    # Keys / connections
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"
    serpapi_api_key: str = ""
    database_url: str = "postgresql://localhost:5432/muse"

    # Pipeline tuning
    embedding_dim: int = 512
    min_images: int = 5
    max_images: int = 30
    max_image_px: int = 768  # downscale cap before processing
    vibe_sample_size: int = 6  # images sent to the vision-LLM
    results_count: int = 40  # ranked pool size; frontend pages through it via "show more"

    # Frontend origin for CORS
    frontend_origin: str = "http://localhost:3000"

    # Public base URL of this API (used for locally-served mock product images)
    api_base_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
