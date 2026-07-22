"""
WEOS Timeline Engine
Version: 0.2.0
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List


@dataclass
class TimelineEvent:
    id: str
    title: str
    timestamp: datetime
    event_type: str
    description: str

    def to_dict(self):
        return asdict(self)


class Timeline:

    def __init__(self):
        self.events: List[TimelineEvent] = []

    def add(self, event: TimelineEvent):
        self.events.append(event)

    def all(self):
        return sorted(
            self.events,
            key=lambda e: e.timestamp
        )

    def count(self):
        return len(self.events)

    def latest(self):
        if not self.events:
            return None

        return max(
            self.events,
            key=lambda e: e.timestamp
        )


if __name__ == "__main__":

    timeline = Timeline()

    timeline.add(
        TimelineEvent(
            id="E001",
            title="Gold Price Increased",
            timestamp=datetime.now(),
            event_type="Market",
            description="Gold price reached a new high."
        )
    )

    print(timeline.count())

    print(timeline.latest().to_dict())
