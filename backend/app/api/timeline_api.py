"""
WEOS Timeline API
Version: 0.5.0
"""

from fastapi import APIRouter

from app.repositories.timeline_repository import TimelineRepository
from app.models.timeline_model import TimelineEventModel

router = APIRouter(
    prefix="/timeline",
    tags=["Timeline"]
)

repository = TimelineRepository()


@router.get("/")
def get_events():
    return repository.all()


@router.get("/type/{event_type}")
def get_by_type(event_type: str):
    return repository.by_type(event_type)


@router.post("/")
def create_event(event: TimelineEventModel):
    repository.save(event)
    return {
        "message": "Timeline event created",
        "event": event
    }


@router.get("/count")
def count_events():
    return {
        "count": repository.count()
    }
