import json
import traceback
import asyncio
from typing import Dict, Any, Callable
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logger import LoggerService
from app.schemas import ItemCreate, ItemUpdate

logger = LoggerService.get_logger(__name__)

class KafkaService:
    def __init__(self):
        self.producer: KafkaProducer | None = None
        self.initialization_lock: asyncio.Lock = asyncio.Lock()

    async def initialize_producer(self, max_retries: int = 5, retry_delay: int = 5) -> None:
        async with self.initialization_lock:
            if self.producer is None:
                for attempt in range(max_retries):
                    try:
                        self.producer = KafkaProducer(
                            bootstrap_servers=[settings.KAFKA_BROKER],
                            value_serializer=lambda v: json.dumps(v).encode('utf-8')
                        )
                        LoggerService.info(logger, "Kafka producer initialized.")
                        return
                    except KafkaError as e:
                        LoggerService.warning(logger, f"Failed to initialize Kafka producer (attempt {attempt + 1}/{max_retries}): {e}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                        else:
                            LoggerService.error(logger, f"Failed to initialize Kafka producer after {max_retries} attempts.")
                            self.producer = None

    async def produce_message(self, topic: str, message: Dict[str, Any]) -> None:
        if self.producer is None:
            raise RuntimeError("Kafka producer is not initialized. Call initialize_producer first.")
        try:
            future = self.producer.send(topic, message)
            future.get(timeout=10)
            LoggerService.info(logger, f"Message sent to topic {topic}")
        except Exception as e:
            LoggerService.error(logger, f"Kafka Produce Error: {e}")
            raise

    async def consume_messages(self, create_item_func: Callable, update_item_func: Callable) -> None:
        consumer = KafkaConsumer(
            settings.KAFKA_ITEM_CREATED_TOPIC,
            settings.KAFKA_ITEM_UPDATED_TOPIC,
            bootstrap_servers=[settings.KAFKA_BROKER],
            group_id="inventory-consumer-group",
            auto_offset_reset='earliest',
            enable_auto_commit=False,
        )

        try:
            for message in consumer:
                LoggerService.info(logger, "Waiting for new messages...")
                topic: str = message.topic
                decoded_message: Dict[str, Any] = json.loads(message.value.decode('utf-8'))

                with SessionLocal() as db:
                    try:
                        if topic == settings.KAFKA_ITEM_CREATED_TOPIC:
                            self.handle_item_created(db, decoded_message, create_item_func)
                        elif topic == settings.KAFKA_ITEM_UPDATED_TOPIC:
                            self.handle_item_updated(db, decoded_message, update_item_func)

                        consumer.commit()
                    except Exception as e:
                        db.rollback()
                        LoggerService.error(logger, f"Processing Error: {e}")
                        LoggerService.error(logger, traceback.format_exc())

        except KeyboardInterrupt:
            LoggerService.info(logger, "Closing Kafka consumer")
            consumer.close()

    @staticmethod
    def handle_item_created(db: Session, message: Dict[str, Any], create_item_func: Callable) -> None:
        item_create = ItemCreate(
            name=message.get('name'),
            description=message.get('description')
        )
        created_item = create_item_func(db, item_create)
        LoggerService.info(logger, f"Item Created: {created_item.id}")

    @staticmethod
    def handle_item_updated(db: Session, message: Dict[str, Any], update_item_func: Callable) -> None:
        item_id: int = message.get('id')
        item_update = ItemUpdate(
            name=message.get('name'),
            description=message.get('description')
        )
        updated_item = update_item_func(db, item_id, item_update)
        if updated_item:
            LoggerService.info(logger, f"Item Updated: {item_id}")
        else:
            LoggerService.warning(logger, f"Item Not Found: {item_id}")

kafka_service = KafkaService()

async def get_kafka_service() -> KafkaService:
    if kafka_service.producer is None:
        await kafka_service.initialize_producer()
    return kafka_service
