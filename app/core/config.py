import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/inventory")
    KAFKA_BROKER: str = os.getenv("KAFKA_BROKER", "kafka:29092")
    KAFKA_ITEM_CREATED_TOPIC: str = "item_created"
    KAFKA_ITEM_UPDATED_TOPIC: str = "item_updated"

    class Config:
        env_file = ".env"

settings = Settings()