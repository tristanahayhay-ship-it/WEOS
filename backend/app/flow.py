"""
WEOS Flow Engine
Version: 0.1.0
"""

from dataclasses import dataclass


@dataclass
class Flow:
    id: str
    source: str
    target: str
    flow_type: str
    quantity: float
    unit: str

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "flow_type": self.flow_type,
            "quantity": self.quantity,
            "unit": self.unit,
        }


if __name__ == "__main__":

    flow = Flow(
        id="FLOW-001",
        source="Vietnam",
        target="USA",
        flow_type="Export",
        quantity=5000,
        unit="Containers"
    )

    print(flow.to_dict())
