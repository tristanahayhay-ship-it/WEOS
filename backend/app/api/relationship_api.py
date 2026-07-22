"""
WEOS Relationship API
Version: 0.9.0
"""

from fastapi import APIRouter
from app.db.relationship import Relationship
from app.services.relationship_service import RelationshipService

router = APIRouter(
    prefix="/relationships",
    tags=["Relationships"]
)

service = RelationshipService()


@router.get("/")
def get_all_relationships():
    return service.get_all()


@router.get("/{relationship_id}")
def get_relationship(relationship_id: str):
    return service.get(relationship_id)


@router.post("/")
def create_relationship(relationship: Relationship):
    return service.create(relationship)


@router.put("/")
def update_relationship(relationship: Relationship):
    return service.update(relationship)


@router.delete("/{relationship_id}")
def delete_relationship(relationship_id: str):
    return service.delete(relationship_id)
