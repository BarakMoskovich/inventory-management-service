from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ItemCreate, ItemUpdate, ItemResponse
from app.services.items_service import (
    delete_item as delete_item_service,
    produce_item_creation_event,
    get_item_by_id,
    get_items,
    produce_item_update_event,
)
from app.services.kafka_service import get_kafka_service, KafkaService
from app.core.logger import LoggerService

router = APIRouter(prefix="/items", tags=["items"])
logger = LoggerService.get_logger(__name__)

def handle_exception(operation: str, e: Exception) -> None:
    LoggerService.error(logger, f"Error during {operation}: {str(e)}")
    if isinstance(e, HTTPException):
        raise e
    raise HTTPException(status_code=500, detail=f"An error occurred during {operation}")

# GET all items
@router.get("/", response_model=List[ItemResponse])
def read_items(db: Session = Depends(get_db)) -> List[ItemResponse]:
    try:
        all_items = get_items(db)
        LoggerService.info(logger, f"Retrieved {len(all_items)} items")
        return all_items
    except Exception as e:
        handle_exception("items retrieval", e)

# GET item by ID
@router.get("/{id}", response_model=ItemResponse)
def read_item(id: int, db: Session = Depends(get_db)) -> ItemResponse:
    try:
        item = get_item_by_id(db, id)
        if not item:
            LoggerService.warning(logger, f"Item with id {id} not found")
            raise HTTPException(status_code=404, detail="Item not found")
        LoggerService.info(logger, f"Retrieved item with id {id}")
        return item
    except Exception as e:
        handle_exception(f"retrieval of item {id}", e)

# POST new item
@router.post("/", status_code=202)
async def create_new_item(item: ItemCreate, kafka_service: KafkaService = Depends(get_kafka_service)) -> dict:
    try:
        await produce_item_creation_event(kafka_service, item)
        LoggerService.info(logger, f"Item creation event produced for {item.name}")
        return {"detail": "Item creation event produced"}
    except Exception as e:
        handle_exception("item creation", e)

# PUT update item
@router.put("/{id}", status_code=202)
async def update_item(id: int, item: ItemUpdate, kafka_service: KafkaService = Depends(get_kafka_service)) -> dict:
    try:
        await produce_item_update_event(kafka_service, id, item)

        LoggerService.info(logger, f"Item update event produced for item {id}")
        return {"detail": "Item update event produced"}
    except Exception as e:
        handle_exception(f"update of item {id}", e)

# DELETE item
@router.delete("/{id}")
def delete_item(id: int, db: Session = Depends(get_db)) -> dict:
    try:
        item = delete_item_service(db, id)
        if not item:
            LoggerService.warning(logger, f"Item with id {id} not found")
            raise HTTPException(status_code=404, detail="Item not found")

        LoggerService.info(logger, f"Deleted item with id {id}")
        return {"detail": "Item deleted"}
    except Exception as e:
        handle_exception(f"deletion of item {id}", e)
