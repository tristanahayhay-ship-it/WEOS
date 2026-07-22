from sqlalchemy.orm import Session

from app.db.entity import Entity


class EntityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, entity: Entity) -> Entity:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get_by_id(self, entity_id: int) -> Entity | None:
        return (
            self.db.query(Entity)
            .filter(Entity.id == entity_id)
            .first()
        )

    def get_all(self) -> list[Entity]:
        return self.db.query(Entity).all()
