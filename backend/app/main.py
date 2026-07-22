"""
WEOS Main Application
Version: 0.9.0
"""

from fastapi import FastAPI

from app.api.entity_api import router as entity_router
from app.api.relationship_api import router as relationship_router
from app.api.flow_api import router as flow_router
from app.api.timeline_api import router as timeline_router

app = FastAPI(
    title="WEOS",
    version="0.9.0"
)

app.include_router(entity_router)
app.include_router(relationship_router)
app.include_router(flow_router)
app.include_router(timeline_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to WEOS API",
        "version": "0.9.0"
    }
