"""
WEOS Relationship Engine
Version: 0.1.0
"""

from dataclasses import dataclass


@dataclass
class Relationship:
    source_id: str
    target_id: str
    relationship_type: str
    description: str = ""

    def to_dict(self):
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.relationship_type,
            "description": self.description,
        }


if __name__ == "__main__":

    relation = Relationship(
        source_id="VN",
        target_id="USA",
        relationship_type="Trade",
        description="Vietnam exports goods to USA"
    )

    print(relation.to_dict())
