"""
WEOS Entity API
Version: 0.9.0
"""

from fastapi import APIRouter
from app.db.entity import Entity
from app.services.entity_service import EntityService

router = APIRouter(
    prefix="/entities",
    tags=["Entities"]
)

service = EntityService()


@router.get("/")
def get_all_entities():
    return service.get_all()


@router.get("/{entity_id}")
def get_entity(entity_id: str):
    return service.get(entity_id)


@router.post("/")
def create_entity(entity: Entity):
    return service.create(entity)


@router.put("/")
def update_entity(entity: Entity):
    return service.update(entity)


@router.delete("/{entity_id}")
def delete_entity(entity_id: str):
    return service.delete(entity_id)
