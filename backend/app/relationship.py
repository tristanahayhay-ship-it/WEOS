"""
WEOS Relationship Engine
Version: 0.2.0
"""

from dataclasses import dataclass, asdict
from typing import List


@dataclass
class Relationship:
    source_id: str
    target_id: str
    relationship_type: str
    description: str = ""

    def to_dict(self):
        return asdict(self)


class RelationshipManager:

    def __init__(self):
        self.relationships: List[Relationship] = []

    def add(self, relationship: Relationship):
        self.relationships.append(relationship)

    def all(self):
        return self.relationships

    def count(self):
        return len(self.relationships)

    def get_from(self, source_id: str):
        return [
            r for r in self.relationships
            if r.source_id == source_id
        ]

    def get_to(self, target_id: str):
        return [
            r for r in self.relationships
            if r.target_id == target_id
        ]


if __name__ == "__main__":

    manager = RelationshipManager()

    manager.add(
        Relationship(
            source_id="VN",
            target_id="US",
            relationship_type="Trade",
            description="Vietnam exports goods to USA"
        )
    )

    print(manager.count())

    for relation in manager.all():
        print(relation.to_dict())
