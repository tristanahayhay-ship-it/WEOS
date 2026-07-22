"""
WEOS Relationship Service
Version: 0.8.0
"""

from app.db.relationship import Relationship
from app.repositories.relationship_repository import RelationshipRepository


class RelationshipService:
    def __init__(self):
        self.repository = RelationshipRepository()

    def get_all(self):
        return self.repository.all()

    def get(self, relationship_id: str):
        return self.repository.get(relationship_id)

    def create(self, relationship: Relationship):
        return self.repository.create(relationship)

    def update(self, relationship: Relationship):
        return self.repository.update(relationship)

    def delete(self, relationship_id: str):
        return self.repository.delete(relationship_id)
