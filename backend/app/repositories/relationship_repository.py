"""
WEOS Relationship Repository
Version: 0.7.0
"""

from sqlalchemy.orm import Session

from app.core.postgres import SessionLocal
from app.db.relationship import Relationship


class RelationshipRepository:

    def get_db(self) -> Session:
        return SessionLocal()

    def all(self):
        db = self.get_db()
        try:
            return db.query(Relationship).all()
        finally:
            db.close()

    def get(self, relationship_id: int):
        db = self.get_db()
        try:
            return (
                db.query(Relationship)
                .filter(Relationship.id == relationship_id)
                .first()
            )
        finally:
            db.close()

    def by_source(self, source_id: str):
        db = self.get_db()
        try:
            return (
                db.query(Relationship)
                .filter(Relationship.source_id == source_id)
                .all()
            )
        finally:
            db.close()

    def by_target(self, target_id: str):
        db = self.get_db()
        try:
            return (
                db.query(Relationship)
                .filter(Relationship.target_id == target_id)
                .all()
            )
        finally:
            db.close()

    def create(self, relationship: Relationship):
        db = self.get_db()
        try:
            db.add(relationship)
            db.commit()
            db.refresh(relationship)
            return relationship
        finally:
            db.close()

    def update(self, relationship: Relationship):
        db = self.get_db()
        try:
            db.merge(relationship)
            db.commit()
            return relationship
        finally:
            db.close()

    def delete(self, relationship_id: int):
        db = self.get_db()
        try:
            relationship = (
                db.query(Relationship)
                .filter(Relationship.id == relationship_id)
                .first()
            )

            if relationship:
                db.delete(relationship)
                db.commit()

            return relationship
        finally:
            db.close()
