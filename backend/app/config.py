from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/productivity"
    REDIS_URL: str = "redis://localhost:6379"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    NGROK_AUTHTOKEN: str = ""

    DEFAULT_USER_EMAIL: str = "user@example.com"
    SECRET_KEY: str = "changeme-super-secret-key-32chars"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
