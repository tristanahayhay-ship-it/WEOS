"""
WEOS Flow Repository
Version: 0.4.0
"""

from typing import List

from app.models.flow_model import FlowModel


class FlowRepository:

    def __init__(self):
        self.flows: List[FlowModel] = []

    def save(self, flow: FlowModel):
        self.flows.append(flow)

    def all(self) -> List[FlowModel]:
        return self.flows

    def by_source(self, source: str) -> List[FlowModel]:
        return [
            f
            for f in self.flows
            if f.source == source
        ]

    def by_target(self, target: str) -> List[FlowModel]:
        return [
            f
            for f in self.flows
            if f.target == target
        ]

    def by_type(self, flow_type: str) -> List[FlowModel]:
        return [
            f
            for f in self.flows
            if f.flow_type == flow_type
        ]

    def count(self):
        return len(self.flows)

    def clear(self):
        self.flows.clear()
