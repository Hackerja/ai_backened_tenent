from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Backend"
    debug: bool = False
    database_url: AnyUrl
    jwt_sec_key: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    supabase_url: str
    supabase_secret_key: str

    @property
    def async_database_url(self) -> str:
        url = str(self.database_url)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()