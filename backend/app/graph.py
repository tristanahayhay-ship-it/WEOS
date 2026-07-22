"""
WEOS Graph Engine
Version: 0.2.0
"""

from typing import Dict, List

from app.entity import Entity, EntityManager
from app.relationship import Relationship, RelationshipManager
from app.flow import Flow, FlowManager
from app.timeline import Timeline, TimelineEvent


class GraphEngine:

    def __init__(self):

        self.entities = EntityManager()

        self.relationships = RelationshipManager()

        self.flows = FlowManager()

        self.timeline = Timeline()

    # =========================
    # Entity
    # =========================

    def add_entity(self, entity: Entity):
        self.entities.add(entity)

    def get_entity(self, entity_id: str):
        return self.entities.get(entity_id)

    def get_entities(self):
        return self.entities.all()

    # =========================
    # Relationship
    # =========================

    def add_relationship(self, relationship: Relationship):
        self.relationships.add(relationship)

    def get_relationships(self):
        return self.relationships.all()

    # =========================
    # Flow
    # =========================

    def add_flow(self, flow: Flow):
        self.flows.add(flow)

    def get_flows(self):
        return self.flows.all()

    # =========================
    # Timeline
    # =========================

    def add_event(self, event: TimelineEvent):
        self.timeline.add(event)

    def get_events(self):
        return self.timeline.all()

    # =========================
    # Statistics
    # =========================

    def statistics(self):

        return {
            "entities": self.entities.count(),
            "relationships": self.relationships.count(),
            "flows": self.flows.count(),
            "events": self.timeline.count()
        }

    # =========================
    # Reset
    # =========================

    def clear(self):

        self.entities = EntityManager()

        self.relationships = RelationshipManager()

        self.flows = FlowManager()

        self.timeline = Timeline()

    # =========================
    # System Info
    # =========================

    def info(self):

        return {
            "system": "WEOS",
            "engine": "Economic Graph",
            "version": "0.2.0"
        }


if __name__ == "__main__":

    graph = GraphEngine()

    print(graph.info())

    print(graph.statistics())
