"""
WEOS Flow Engine
Version: 0.2.0
"""

from dataclasses import dataclass, asdict
from typing import List


@dataclass
class Flow:
    id: str
    source: str
    target: str
    flow_type: str
    quantity: float
    unit: str

    def to_dict(self):
        return asdict(self)


class FlowManager:

    def __init__(self):
        self.flows: List[Flow] = []

    def add(self, flow: Flow):
        self.flows.append(flow)

    def all(self):
        return self.flows

    def count(self):
        return len(self.flows)

    def get_by_source(self, source: str):
        return [
            f for f in self.flows
            if f.source == source
        ]

    def get_by_target(self, target: str):
        return [
            f for f in self.flows
            if f.target == target
        ]


if __name__ == "__main__":

    manager = FlowManager()

    manager.add(
        Flow(
            id="F001",
            source="Vietnam",
            target="USA",
            flow_type="Export",
            quantity=500000,
            unit="USD"
        )
    )

    print(manager.count())

    for flow in manager.all():
        print(flow.to_dict())
