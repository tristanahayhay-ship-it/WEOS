from app.core.database import database


def connect_neo4j() -> None:
    database.connection = "Neo4j Connected"
