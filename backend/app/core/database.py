"""
WEOS Database Core
Version: 0.3.0
"""

from app.core.config import settings


class Database:

    def __init__(self):

        self.postgres = {
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
            "database": settings.POSTGRES_DB,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD,
        }

        self.neo4j = {
            "uri": settings.NEO4J_URI,
            "user": settings.NEO4J_USER,
            "password": settings.NEO4J_PASSWORD,
        }

    def postgres_info(self):
        return self.postgres

    def neo4j_info(self):
        return self.neo4j


database = Database()
