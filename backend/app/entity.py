"""
WEOS Entity Engine
Version: 0.2.0
"""

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class Entity:
    id: str
    name: str
    entity_type: str
    country: str
    latitude: float
    longitude: float

    def to_dict(self):
        return asdict(self)


class EntityManager:

    def __init__(self):
        self.entities: Dict[str, Entity] = {}

    def add(self, entity: Entity):
        self.entities[entity.id] = entity

    def remove(self, entity_id: str):
        if entity_id in self.entities:
            del self.entities[entity_id]

    def get(self, entity_id: str):
        return self.entities.get(entity_id)

    def all(self) -> List[Entity]:
        return list(self.entities.values())

    def count(self):
        return len(self.entities)

    def exists(self, entity_id: str):
        return entity_id in self.entities


if __name__ == "__main__":

    manager = EntityManager()

    manager.add(
        Entity(
            id="VN",
            name="Vietnam",
            entity_type="Country",
            country="Vietnam",
            latitude=16.0,
            longitude=108.0,
        )
    )

    print(manager.count())
    print(manager.get("VN").to_dict())
