"""
WEOS Timeline Service
Version: 0.8.0
"""

from app.db.timeline import TimelineEvent
from app.repositories.timeline_repository import TimelineRepository


class TimelineService:
    def __init__(self):
        self.repository = TimelineRepository()

    def get_all(self):
        return self.repository.all()

    def get(self, timeline_id: str):
        return self.repository.get(timeline_id)

    def create(self, event: TimelineEvent):
        return self.repository.create(event)

    def update(self, event: TimelineEvent):
        return self.repository.update(event)

    def delete(self, timeline_id: str):
        return self.repository.delete(timeline_id)
