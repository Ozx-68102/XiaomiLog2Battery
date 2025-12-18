import sqlite3

from src.config import ANALYSIS_RESULTS_FIELDS
from .connect import BaseStorage


class AnalysisResults(BaseStorage):
    def __init__(self) -> None:
        super().__init__()
        self.table_field = ANALYSIS_RESULTS_FIELDS

    def init_table(self) -> None:
        """
        Use a series of SQL statements to initialize table called **analysis_results**.
        If table exists, its data will be overwritten (drop & create).
        """

        init_statement = """
                         DROP TABLE IF EXISTS analysis_results;
                         CREATE TABLE analysis_results
                         (
                             id                            INTEGER PRIMARY KEY AUTOINCREMENT,
                             log_capture_time              INTEGER NOT NULL,
                             estimated_battery_capacity    INTEGER NOT NULL,
                             last_learned_battery_capacity INTEGER NOT NULL,
                             min_learned_battery_capacity  INTEGER NOT NULL,
                             max_learned_battery_capacity  INTEGER NOT NULL,
                             phone_brand                   TEXT    NOT NULL COLLATE BINARY,
                             nickname                      TEXT    NOT NULL COLLATE BINARY,
                             system_version                TEXT    NOT NULL COLLATE BINARY,
                             design_capacity               INTEGER NOT NULL,
                             cycle_count                   INTEGER NOT NULL,
                             hardware_capacity             INTEGER NOT NULL
                         );
                         CREATE INDEX IF NOT EXISTS idx_log_capture_time
                             ON analysis_results (log_capture_time);
                         CREATE UNIQUE INDEX IF NOT EXISTS idx_uni_log
                             ON analysis_results (log_capture_time, nickname);
                         """

        with self.conn as c:
            cur = c.cursor()
            cur.executescript(init_statement)

    def save_data(self, data: list[dict[str, str | int]]) -> int:
        """
        Insert rows of battery analysis results into the table **analysis_results**.

        Parameters
        ----------
        data: list[dict[str, str | int]]
            A list of dictionaries containing keys of `TABLE_FIELDS`.

            - log_capture_time : int
            - estimated_battery_capacity : int
            - last_learned_battery_capacity : int
            - min_learned_battery_capacity : int
            - max_learned_battery_capacity : int
            - phone_brand : str
            - nickname : str
            - system_version : str
            - cycle_count : int
            - hardware_capacity : int

        Returns
        -------
        int
            The number of rows inserted successfully.
        """

        fields_str = ", ".join(self.table_field)
        placeholders_str = ", ".join(["?"] * len(self.table_field))

        counts = 0

        with self.conn as c:
            cur = c.cursor()
            cur.executemany(
                f"INSERT INTO analysis_results ({fields_str}) VALUES ({placeholders_str})",
                [[item[fields] for fields in self.table_field] for item in data]
            )

            counts = cur.rowcount

        return counts

    def get_unique_model(self) -> list[str] | None:
        results = None
        with self.conn as c:
            c.row_factory = sqlite3.Row
            cur = c.cursor()
            cur.execute("SELECT DISTINCT nickname FROM analysis_results")
            results = [row[0] for row in cur.fetchall()]

        return results if results else None

    def get_results(self, model: str | None = None) -> list[dict[str, str | int]] | None:
        results = None

        statements = "SELECT * FROM analysis_results"
        if model:
            statements += f" WHERE nickname = '{model}'"
        statements += " ORDER BY log_capture_time DESC;"

        with self.conn as c:
            c.row_factory = sqlite3.Row
            cur = c.cursor()
            cur.execute(statements)
            results = [dict(row) for row in cur.fetchall()]

        return results if results else None
