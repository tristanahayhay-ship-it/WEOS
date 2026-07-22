"""
WEOS Timeline API
Version: 0.9.0
"""

from fastapi import APIRouter
from app.db.timeline import TimelineEvent
from app.services.timeline_service import TimelineService

router = APIRouter(
    prefix="/timeline",
    tags=["Timeline"]
)

service = TimelineService()


@router.get("/")
def get_all_events():
    return service.get_all()


@router.get("/{timeline_id}")
def get_event(timeline_id: str):
    return service.get(timeline_id)


@router.post("/")
def create_event(event: TimelineEvent):
    return service.create(event)


@router.put("/")
def update_event(event: TimelineEvent):
    return service.update(event)


@router.delete("/{timeline_id}")
def delete_event(timeline_id: str):
    return service.delete(timeline_id)
