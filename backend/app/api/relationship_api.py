"""
WEOS Relationship API
Version: 0.5.0
"""

from fastapi import APIRouter

from app.repositories.relationship_repository import RelationshipRepository
from app.models.relationship_model import RelationshipModel

router = APIRouter(
    prefix="/relationships",
    tags=["Relationships"]
)

repository = RelationshipRepository()


@router.get("/")
def get_relationships():
    return repository.all()


@router.get("/source/{source_id}")
def get_by_source(source_id: str):
    return repository.by_source(source_id)


@router.get("/target/{target_id}")
def get_by_target(target_id: str):
    return repository.by_target(target_id)


@router.post("/")
def create_relationship(relationship: RelationshipModel):
    repository.save(relationship)
    return {
        "message": "Relationship created",
        "relationship": relationship
    }


@router.get("/count")
def count_relationships():
    return {
        "count": repository.count()
    }
