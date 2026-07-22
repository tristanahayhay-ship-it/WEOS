"""
WEOS Timeline Model
Version: 0.3.0
"""

from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TimelineEventModel:

    id: str

    title: str

    timestamp: datetime

    event_type: str

    description: str

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
