"""
WEOS Entity Model
Version: 0.3.0
"""

from dataclasses import dataclass, asdict


@dataclass
class EntityModel:

    id: str

    name: str

    entity_type: str

    country: str

    latitude: float

    longitude: float

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
