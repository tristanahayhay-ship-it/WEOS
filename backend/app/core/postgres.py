from app.core.database import database


def connect_postgres() -> None:
    database.connection = "PostgreSQL Connected"
