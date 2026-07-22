"""
WEOS Database Engine
Version: 0.1.0
"""

from typing import List
from app.entity import Entity


class Database:

    def __init__(self):
        self.entities: List[Entity] = []

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def get_all_entities(self):
        return self.entities

    def find_by_id(self, entity_id: str):
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None


if __name__ == "__main__":

    db = Database()

    vietnam = Entity(
        id="VN",
        name="Vietnam",
        entity_type="Country",
        country="Vietnam",
        latitude=16.0,
        longitude=108.0
    )

    db.add_entity(vietnam)

    print(db.get_all_entities())
