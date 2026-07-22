"""
WEOS Relationship Database Model
Version: 0.6.0
"""

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.core.postgres import Base


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)

    source_id = Column(String, nullable=False)

    target_id = Column(String, nullable=False)

    relationship_type = Column(String, nullable=False)

    description = Column(String)
