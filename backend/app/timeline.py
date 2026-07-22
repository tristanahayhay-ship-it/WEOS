"""
WEOS Timeline Engine
Version: 0.1.0
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimelineEvent:
    id: str
    title: str
    timestamp: datetime
    event_type: str
    description: str

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "description": self.description,
        }


if __name__ == "__main__":

    event = TimelineEvent(
        id="EVENT-001",
        title="Fed Interest Rate Decision",
        timestamp=datetime.now(),
        event_type="Monetary Policy",
        description="Federal Reserve keeps interest rates unchanged."
    )

    print(event.to_dict())
