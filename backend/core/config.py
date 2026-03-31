from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = ""
    openai_api_key: str = ""

    model_config = {"env_file": "../.env"}

settings = Settings()
os.environ["OPENAI_API_KEY"] = settings.openai_api_key
