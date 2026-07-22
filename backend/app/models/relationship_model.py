"""
WEOS Relationship Model
Version: 0.3.0
"""

from dataclasses import dataclass, asdict


@dataclass
class RelationshipModel:

    source_id: str

    target_id: str

    relationship_type: str

    description: str = ""

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
