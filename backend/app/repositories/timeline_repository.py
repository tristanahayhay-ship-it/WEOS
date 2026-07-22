"""
WEOS Timeline Repository
Version: 0.7.0
"""

from sqlalchemy.orm import Session

from app.core.postgres import SessionLocal
from app.db.timeline import TimelineEvent


class TimelineRepository:

    def get_db(self) -> Session:
        return SessionLocal()

    def all(self):
        db = self.get_db()
        try:
            return db.query(TimelineEvent).all()
        finally:
            db.close()

    def get(self, event_id: int):
        db = self.get_db()
        try:
            return (
                db.query(TimelineEvent)
                .filter(TimelineEvent.id == event_id)
                .first()
            )
        finally:
            db.close()

    def by_type(self, event_type: str):
        db = self.get_db()
        try:
            return (
                db.query(TimelineEvent)
                .filter(TimelineEvent.event_type == event_type)
                .all()
            )
        finally:
            db.close()

    def create(self, event: TimelineEvent):
        db = self.get_db()
        try:
            db.add(event)
            db.commit()
            db.refresh(event)
            return event
        finally:
            db.close()

    def update(self, event: TimelineEvent):
        db = self.get_db()
        try:
            db.merge(event)
            db.commit()
            return event
        finally:
            db.close()

    def delete(self, event_id: int):
        db = self.get_db()
        try:
            event = (
                db.query(TimelineEvent)
                .filter(TimelineEvent.id == event_id)
                .first()
            )

            if event:
                db.delete(event)
                db.commit()

            return event
        finally:
            db.close()
