"""
WEOS Flow Repository
Version: 0.7.0
"""

from sqlalchemy.orm import Session

from app.core.postgres import SessionLocal
from app.db.flow import Flow


class FlowRepository:

    def get_db(self) -> Session:
        return SessionLocal()

    def all(self):
        db = self.get_db()
        try:
            return db.query(Flow).all()
        finally:
            db.close()

    def get(self, flow_id: int):
        db = self.get_db()
        try:
            return (
                db.query(Flow)
                .filter(Flow.id == flow_id)
                .first()
            )
        finally:
            db.close()

    def by_source(self, source: str):
        db = self.get_db()
        try:
            return (
                db.query(Flow)
                .filter(Flow.source == source)
                .all()
            )
        finally:
            db.close()

    def by_target(self, target: str):
        db = self.get_db()
        try:
            return (
                db.query(Flow)
                .filter(Flow.target == target)
                .all()
            )
        finally:
            db.close()

    def create(self, flow: Flow):
        db = self.get_db()
        try:
            db.add(flow)
            db.commit()
            db.refresh(flow)
            return flow
        finally:
            db.close()

    def update(self, flow: Flow):
        db = self.get_db()
        try:
            db.merge(flow)
            db.commit()
            return flow
        finally:
            db.close()

    def delete(self, flow_id: int):
        db = self.get_db()
        try:
            flow = (
                db.query(Flow)
                .filter(Flow.id == flow_id)
                .first()
            )

            if flow:
                db.delete(flow)
                db.commit()

            return flow
        finally:
            db.close()
