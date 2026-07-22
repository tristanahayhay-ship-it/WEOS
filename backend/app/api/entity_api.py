"""
WEOS Entity API
Version: 0.5.0
"""

from fastapi import APIRouter

from app.repositories.entity_repository import EntityRepository
from app.models.entity_model import EntityModel

router = APIRouter(
    prefix="/entities",
    tags=["Entities"]
)

repository = EntityRepository()


@router.get("/")
def get_entities():
    return repository.all()


@router.get("/{entity_id}")
def get_entity(entity_id: str):
    return repository.get(entity_id)


@router.post("/")
def create_entity(entity: EntityModel):
    repository.save(entity)
    return {
        "message": "Entity created",
        "entity": entity
    }


@router.delete("/{entity_id}")
def delete_entity(entity_id: str):
    repository.delete(entity_id)
    return {
        "message": "Entity deleted"
    }
