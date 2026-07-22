from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    source_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id"),
        nullable=False,
    )

    target_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id"),
        nullable=False,
    )

    relation: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
