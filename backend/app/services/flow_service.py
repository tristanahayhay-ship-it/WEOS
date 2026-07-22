"""
WEOS Flow Service
Version: 0.8.0
"""

from app.db.flow import Flow
from app.repositories.flow_repository import FlowRepository


class FlowService:
    def __init__(self):
        self.repository = FlowRepository()

    def get_all(self):
        return self.repository.all()

    def get(self, flow_id: str):
        return self.repository.get(flow_id)

    def create(self, flow: Flow):
        return self.repository.create(flow)

    def update(self, flow: Flow):
        return self.repository.update(flow)

    def delete(self, flow_id: str):
        return self.repository.delete(flow_id)
