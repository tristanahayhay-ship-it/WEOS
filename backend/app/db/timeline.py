from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Timeline(Base):
    __tablename__ = "timelines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id"),
        nullable=False,
    )

    timestamp: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
    )
