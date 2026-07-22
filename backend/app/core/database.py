from typing import Optional


class Database:
    def __init__(self) -> None:
        self.connection: Optional[object] = None


database = Database()
