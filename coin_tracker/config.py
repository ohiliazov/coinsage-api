from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    fernet_key: str

    class Config:
        env_file = ".env"


settings = Settings()
settings.database_url = settings.database_url.replace(
    "postgres://", "postgresql://"
)
