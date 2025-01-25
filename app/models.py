from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Item(Base):
    __tablename__ = 'items'
    __table_args__ = {'schema': 'inventory'}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
