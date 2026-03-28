from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "postgresql://fte_user:password@localhost:5432/fte_db"
    openai_api_key: str = ""

    model_config = {"env_file": "../.env"}

settings = Settings()
