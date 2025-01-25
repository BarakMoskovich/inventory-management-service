from typing import Generator
from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.core.logger import LoggerService

logger = LoggerService.get_logger(__name__)

LoggerService.info(logger, "Creating database engine")
engine = create_engine(settings.DATABASE_URL)

LoggerService.info(logger, "Configuring session maker")
SessionLocal: sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    LoggerService.info(logger, "Creating a new database session")
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        LoggerService.info(logger, "Closing the database session")
        db.close()