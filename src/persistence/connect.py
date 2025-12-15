import sqlite3

from src.config import DB_PATH


class BaseStorage:
    def __init__(self) -> None:
        DB_PATH.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)

    def close(self) -> None:
        self.conn.close()

    def __del__(self) -> None:
        self.close()