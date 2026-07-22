"""
WEOS Entity Repository
Version: 0.4.0
"""

from typing import Dict, List

from app.models.entity_model import EntityModel


class EntityRepository:

    def __init__(self):
        self.entities: Dict[str, EntityModel] = {}

    def save(self, entity: EntityModel):
        self.entities[entity.id] = entity

    def get(self, entity_id: str):
        return self.entities.get(entity_id)

    def all(self) -> List[EntityModel]:
        return list(self.entities.values())

    def delete(self, entity_id: str):
        if entity_id in self.entities:
            del self.entities[entity_id]

    def exists(self, entity_id: str):
        return entity_id in self.entities

    def count(self):
        return len(self.entities)

    def clear(self):
        self.entities.clear()
