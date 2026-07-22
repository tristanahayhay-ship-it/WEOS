"""
WEOS Timeline Repository
Version: 0.4.0
"""

from typing import List

from app.models.timeline_model import TimelineEventModel


class TimelineRepository:

    def __init__(self):
        self.events: List[TimelineEventModel] = []

    def save(self, event: TimelineEventModel):
        self.events.append(event)

    def all(self) -> List[TimelineEventModel]:
        return sorted(
            self.events,
            key=lambda e: e.timestamp
        )

    def by_type(self, event_type: str) -> List[TimelineEventModel]:
        return [
            e
            for e in self.events
            if e.event_type == event_type
        ]

    def count(self):
        return len(self.events)

    def clear(self):
        self.events.clear()
