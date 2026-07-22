"""
WEOS Graph Engine
Version: 0.1.0
"""

from typing import Dict, List

from app.entity import Entity
from app.relationship import Relationship


class Graph:

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []

    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity

    def add_relationship(self, relationship: Relationship):
        self.relationships.append(relationship)

    def get_entity(self, entity_id: str):
        return self.entities.get(entity_id)

    def get_relationships(self, entity_id: str):
        return [
            r for r in self.relationships
            if r.source_id == entity_id or r.target_id == entity_id
        ]


if __name__ == "__main__":

    graph = Graph()

    vietnam = Entity(
        id="VN",
        name="Vietnam",
        entity_type="Country",
        country="Vietnam",
        latitude=16.0,
        longitude=108.0
    )

    usa = Entity(
        id="US",
        name="United States",
        entity_type="Country",
        country="United States",
        latitude=38.0,
        longitude=-97.0
    )

    graph.add_entity(vietnam)
    graph.add_entity(usa)

    graph.add_relationship(
        Relationship(
            source_id="VN",
            target_id="US",
            relationship_type="Trade",
            description="Export"
        )
    )

    print(graph.get_entity("VN"))
    print(graph.get_relationships("VN"))
