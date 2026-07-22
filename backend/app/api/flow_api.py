"""
WEOS Flow API
Version: 0.9.0
"""

from fastapi import APIRouter
from app.db.flow import Flow
from app.services.flow_service import FlowService

router = APIRouter(
    prefix="/flows",
    tags=["Flows"]
)

service = FlowService()


@router.get("/")
def get_all_flows():
    return service.get_all()


@router.get("/{flow_id}")
def get_flow(flow_id: str):
    return service.get(flow_id)


@router.post("/")
def create_flow(flow: Flow):
    return service.create(flow)


@router.put("/")
def update_flow(flow: Flow):
    return service.update(flow)


@router.delete("/{flow_id}")
def delete_flow(flow_id: str):
    return service.delete(flow_id)
