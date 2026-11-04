from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://mongo:27017"
    mongodb_db: str = "va_jobs"
    redis_uri: str = "redis://redis:6379/0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
