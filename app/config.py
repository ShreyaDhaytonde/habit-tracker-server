from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./habits.db"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
