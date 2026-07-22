"""
WEOS Flow API
Version: 0.5.0
"""

from fastapi import APIRouter

from app.repositories.flow_repository import FlowRepository
from app.models.flow_model import FlowModel

router = APIRouter(
    prefix="/flows",
    tags=["Flows"]
)

repository = FlowRepository()


@router.get("/")
def get_flows():
    return repository.all()


@router.get("/source/{source}")
def get_by_source(source: str):
    return repository.by_source(source)


@router.get("/target/{target}")
def get_by_target(target: str):
    return repository.by_target(target)


@router.post("/")
def create_flow(flow: FlowModel):
    repository.save(flow)
    return {
        "message": "Flow created",
        "flow": flow
    }


@router.get("/count")
def count_flows():
    return {
        "count": repository.count()
    }
