"""
WEOS Flow Model
Version: 0.3.0
"""

from dataclasses import dataclass, asdict


@dataclass
class FlowModel:

    id: str

    source: str

    target: str

    flow_type: str

    quantity: float

    unit: str

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
