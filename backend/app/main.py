"""
WEOS Backend
Version: 0.5.0
"""

from fastapi import FastAPI

from app.api.entity_api import router as entity_router
from app.api.relationship_api import router as relationship_router
from app.api.flow_api import router as flow_router
from app.api.timeline_api import router as timeline_router

from app.db.create_tables import create_tables

app = FastAPI(
    title="WEOS",
    version="0.5.0",
    description="World Economic Operating System"
)


@app.get("/")
def root():
    return {
        "name": "WEOS",
        "version": "0.5.0",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


app.include_router(entity_router)
app.include_router(relationship_router)
app.include_router(flow_router)
app.include_router(timeline_router)
