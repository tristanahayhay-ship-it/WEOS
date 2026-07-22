"""
WEOS Timeline Database Model
Version: 0.6.0
"""

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from app.core.postgres import Base


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String, nullable=False)

    event_type = Column(String, nullable=False)

    description = Column(String)

    timestamp = Column(DateTime, nullable=False)
