from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "sqlite:///./habits.db"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://habit-tracker-client-five.vercel.app",
    ]


settings = Settings()
