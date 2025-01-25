from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.models import Item
from app.schemas import ItemCreate, ItemUpdate
from app.services.kafka_service import KafkaService
from app.core.logger import LoggerService

logger = LoggerService.get_logger(__name__)

def get_items(db: Session) -> List[Item]:
    try:
        all_items = db.query(Item).all()
        LoggerService.info(logger, f"Retrieved {len(all_items)} items")
        return all_items
    except SQLAlchemyError as e:
        LoggerService.error(logger, f"Database error while fetching items: {str(e)}")
        raise

def get_item_by_id(db: Session, id: int) -> Optional[Item]:
    try:
        item = db.query(Item).filter(Item.id == id).first()
        if item:
            LoggerService.info(logger, f"Retrieved item with id {id}")
        else:
            LoggerService.warning(logger, f"Item with id {id} not found")
        return item
    except SQLAlchemyError as e:
        LoggerService.error(logger, f"Database error while fetching item {id}: {str(e)}")
        raise

async def produce_item_creation_event(kafka_service: KafkaService, item: ItemCreate) -> None:
    try:
        await kafka_service.produce_message(settings.KAFKA_ITEM_CREATED_TOPIC, {
            "name": item.name,
            "description": item.description,
        })
        LoggerService.info(logger, f"Kafka message produced for item creation: {item.name}")
    except Exception as e:
        LoggerService.error(logger, f"Error producing Kafka message for item creation: {str(e)}")
        raise

async def produce_item_update_event(kafka_service: KafkaService, id: int, item: ItemUpdate) -> None:
    try:
        await kafka_service.produce_message(settings.KAFKA_ITEM_UPDATED_TOPIC, {
            "id": id,
            "name": item.name,
            "description": item.description,
        })
        LoggerService.info(logger, f"Kafka message produced for item update: {id}")
    except Exception as e:
        LoggerService.error(logger, f"Error producing Kafka message for item update: {str(e)}")
        raise

def create_item(db: Session, item: ItemCreate) -> Item:
    try:
        create_item = Item(name=item.name, description=item.description)
        db.add(create_item)
        db.commit()
        db.refresh(create_item)
        LoggerService.info(logger, f"Item created")
        return create_item
    except SQLAlchemyError as e:
        db.rollback()
        LoggerService.error(logger, f"Database error while creating item: {str(e)}")
        raise

def update_item(db: Session, id: int, item: ItemUpdate) -> Optional[Item]:
    try:
        db_item = db.query(Item).filter(Item.id == id).first()
        if not db_item:
            LoggerService.warning(logger, f"Item with id: {id} not found for update")
            return None

        for key, value in item.model_dump(exclude_unset=True).items():
            setattr(db_item, key, value)

        db.commit()
        db.refresh(db_item)
        LoggerService.info(logger, f"Item updated: {id}")
        return db_item
    except SQLAlchemyError as e:
        db.rollback()
        LoggerService.error(logger, f"Database error while updating item {id}: {str(e)}")
        raise

def delete_item(db: Session, id: int) -> Optional[Item]:
    try:
        item = db.query(Item).filter(Item.id == id).first()
        if item:
            db.delete(item)
            db.commit()
            LoggerService.info(logger, f"Item deleted: {id}")
            return item
        else:
            LoggerService.warning(logger, f"Item with id: {id} not found for deletion")
            return None 
    except SQLAlchemyError as e:
        db.rollback()
        LoggerService.error(logger, f"Database error while deleting item {id}: {str(e)}")
        raise
