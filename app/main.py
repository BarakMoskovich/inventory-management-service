from functools import lru_cache
import threading
import asyncio
from typing import Dict
from app.core.config import Settings
from fastapi import FastAPI
from app.routers import items
from app.services.kafka_service import kafka_service
from app.services.items_service import create_item, update_item
from app.core.logger import LoggerService

logger = LoggerService.get_logger(__name__)

# Limit Kafka logs to WARNING level to reduce noise in application logs
LoggerService.get_logger('kafka').setLevel(LoggerService.get_log_level('WARNING'))

app = FastAPI()

@lru_cache()
def get_settings():
    return Settings()

app.include_router(items.router)

def run_kafka_consumer() -> None:
    # Run the Kafka consumer in a separate event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    LoggerService.info(logger, "Starting Kafka consumer in a separate thread")
    try:
        loop.run_until_complete(kafka_service.consume_messages(create_item, update_item))
    except Exception as e:
        LoggerService.error(logger, f"Error in Kafka consumer thread: {e}")
        raise 

@app.on_event("startup")
async def startup_event() -> None:
    try:
        # Initialize Kafka producer
        await kafka_service.initialize_producer()
        LoggerService.info(logger, "Kafka producer initialized successfully")
    except Exception as e:
        LoggerService.error(logger, f"Failed to initialize Kafka producer: {e}")
        raise RuntimeError(f"Error: Could not initialize Kafka producer. {str(e)}")

    try:
        # Start Kafka consumer in a separate thread
        consumer_thread = threading.Thread(target=run_kafka_consumer, daemon=True)
        consumer_thread.start()
        LoggerService.info(logger, "Kafka consumer thread started")
    except Exception as e:
        LoggerService.error(logger, f"Failed to start Kafka consumer thread: {e}")
        raise RuntimeError(f"Error: Could not start Kafka consumer thread. {str(e)}")

@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Inventory Management Service"}
