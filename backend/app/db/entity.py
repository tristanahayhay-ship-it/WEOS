"""
WEOS Entity Database Model
Version: 0.6.0
"""

from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import String

from app.core.postgres import Base


class Entity(Base):
    __tablename__ = "entities"

    id = Column(String, primary_key=True, index=True)

    name = Column(String, nullable=False)

    entity_type = Column(String, nullable=False)

    country = Column(String)

    latitude = Column(Float)

    longitude = Column(Float)
