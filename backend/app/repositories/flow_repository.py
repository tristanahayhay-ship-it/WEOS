from sqlalchemy.orm import Session

from app.db.flow import Flow


class FlowRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, flow: Flow) -> Flow:
        self.db.add(flow)
        self.db.commit()
        self.db.refresh(flow)
        return flow

    def get_by_id(self, flow_id: int) -> Flow | None:
        return (
            self.db.query(Flow)
            .filter(Flow.id == flow_id)
            .first()
        )

    def get_all(self) -> list[Flow]:
        return self.db.query(Flow).all()
