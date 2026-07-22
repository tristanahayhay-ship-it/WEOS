from sqlalchemy.orm import Session

from app.db.relationship import Relationship


class RelationshipRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, relationship: Relationship) -> Relationship:
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        return relationship

    def get_by_id(self, relationship_id: int) -> Relationship | None:
        return (
            self.db.query(Relationship)
            .filter(Relationship.id == relationship_id)
            .first()
        )

    def get_all(self) -> list[Relationship]:
        return self.db.query(Relationship).all()
