"""
WEOS Configuration
Version: 0.3.0
"""

import os


class Settings:

    APP_NAME = "WEOS"

    VERSION = "0.3.0"

    API_PREFIX = "/api"

    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")

    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    POSTGRES_DB = os.getenv("POSTGRES_DB", "weos")

    POSTGRES_USER = os.getenv("POSTGRES_USER", "weos")

    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "weos")

    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")

    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")

    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "weos")


settings = Settings()
