"""
WEOS Relationship Repository
Version: 0.4.0
"""

from typing import List

from app.models.relationship_model import RelationshipModel


class RelationshipRepository:

    def __init__(self):
        self.relationships: List[RelationshipModel] = []

    def save(self, relationship: RelationshipModel):
        self.relationships.append(relationship)

    def all(self) -> List[RelationshipModel]:
        return self.relationships

    def by_source(self, source_id: str) -> List[RelationshipModel]:
        return [
            r
            for r in self.relationships
            if r.source_id == source_id
        ]

    def by_target(self, target_id: str) -> List[RelationshipModel]:
        return [
            r
            for r in self.relationships
            if r.target_id == target_id
        ]

    def count(self):
        return len(self.relationships)

    def clear(self):
        self.relationships.clear()
