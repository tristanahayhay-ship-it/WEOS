"""
WEOS Flow Database Model
Version: 0.6.0
"""

from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from app.core.postgres import Base


class Flow(Base):
    __tablename__ = "flows"

    id = Column(Integer, primary_key=True, autoincrement=True)

    source = Column(String, nullable=False)

    target = Column(String, nullable=False)

    flow_type = Column(String, nullable=False)

    value = Column(Float)

    unit = Column(String)
