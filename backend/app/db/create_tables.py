"""
WEOS Database Table Creator
Version: 0.6.0
"""

from app.core.postgres import Base
from app.core.postgres import engine

# Import tất cả model
from app.db import Entity
from app.db import Relationship
from app.db import Flow
from app.db import TimelineEvent


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("WEOS database tables created successfully.")


if __name__ == "__main__":
    create_tables()
