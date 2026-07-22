"""
WEOS Entity Repository
Version: 0.7.0
"""

from sqlalchemy.orm import Session

from app.core.postgres import SessionLocal
from app.db.entity import Entity


class EntityRepository:

    def get_db(self) -> Session:
        return SessionLocal()

    def all(self):
        db = self.get_db()
        try:
            return db.query(Entity).all()
        finally:
            db.close()

    def get(self, entity_id: str):
        db = self.get_db()
        try:
            return (
                db.query(Entity)
                .filter(Entity.id == entity_id)
                .first()
            )
        finally:
            db.close()

    def create(self, entity: Entity):
        db = self.get_db()
        try:
            db.add(entity)
            db.commit()
            db.refresh(entity)
            return entity
        finally:
            db.close()

    def update(self, entity: Entity):
        db = self.get_db()
        try:
            db.merge(entity)
            db.commit()
            return entity
        finally:
            db.close()

    def delete(self, entity_id: str):
        db = self.get_db()
        try:
            entity = (
                db.query(Entity)
                .filter(Entity.id == entity_id)
                .first()
            )

            if entity:
                db.delete(entity)
                db.commit()

            return entity
        finally:
            db.close()
