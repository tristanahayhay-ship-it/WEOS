"""
WEOS Neo4j Core
Version: 0.6.0
"""

from neo4j import GraphDatabase

from app.core.config import settings


driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(
        settings.NEO4J_USER,
        settings.NEO4J_PASSWORD
    )
)


def get_driver():
    return driver


def close_driver():
    driver.close()


def test_connection():
    with driver.session() as session:
        result = session.run(
            "RETURN 'WEOS Connected Successfully' AS message"
        )
        return result.single()["message"]
