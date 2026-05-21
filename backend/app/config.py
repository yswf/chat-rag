from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://chatrag:chatrag123@db:5432/chatrag"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"

    # Vector search defaults
    top_k: int = 5
    max_history_messages: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
