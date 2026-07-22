"""
WEOS Entity Service
Version: 0.8.0
"""

from app.db.entity import Entity
from app.repositories.entity_repository import EntityRepository


class EntityService:
    def __init__(self):
        self.repository = EntityRepository()

    def get_all(self):
        return self.repository.all()

    def get(self, entity_id: str):
        return self.repository.get(entity_id)

    def create(self, entity: Entity):
        return self.repository.create(entity)

    def update(self, entity: Entity):
        return self.repository.update(entity)

    def delete(self, entity_id: str):
        return self.repository.delete(entity_id)
