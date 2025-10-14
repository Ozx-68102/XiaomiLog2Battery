import os
import sqlite3

from Modules.FileProcess.FolderOperator import INSTANCE_PATH

DB_PATH = os.path.join(INSTANCE_PATH, "database.db")


def _get_connection() -> sqlite3.Connection:
    """
    Open and return a sqlite3 connection.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_database() -> None:
    """
    Initialize the database.
    """
    with _get_connection() as conn:
        cur = conn.cursor()
        create_table_statement = """
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_capture_time TEXT NOT NULL,
            estimated_battery_capacity INTEGER NOT NULL,
            last_learned_battery_capacity INTEGER NOT NULL,
            min_learned_battery_capacity INTEGER NOT NULL,
            max_learned_battery_capacity INTEGER NOT NULL,
            phone_brand TEXT NOT NULL COLLATE BINARY,
            nickname TEXT NOT NULL COLLATE BINARY,
            system_version TEXT NOT NULL COLLATE BINARY
        )
        """
        create_index_statement = """
        CREATE INDEX IF NOT EXISTS idx_log_capture_time
        ON analysis_results (log_capture_time)
        """

        cur.execute(create_table_statement)
        cur.execute(create_index_statement)


def save_data(data: dict[str, str | int]) -> int | None:
    """
    Inserts a new row of battery analysis results into the database.
    :param data: A dictionary containing the following keys: log_capture_time(str), estimated_battery_capacity(int), last_learned_battery_capacity(int), min_learned_battery_capacity(int), max_learned_battery_capacity(int), phone_brand(str), nickname(str), system_version(str)
    :return: The id of the newly inserted record.
    """
    with _get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO analysis_results (
            log_capture_time, estimated_battery_capacity, last_learned_battery_capacity,
            min_learned_battery_capacity, max_learned_battery_capacity, phone_brand, nickname, system_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (data["log_capture_time"], data["estimated_battery_capacity"], data["last_learned_battery_capacity"], data["min_learned_battery_capacity"], data["max_learned_battery_capacity"], data["phone_brand"], data["nickname"], data["system_version"]))

        return cur.lastrowid


def get_all_results() -> list[dict[str, str | int]]:
    """
    Retrieves all analysis results from the database, ordered by capture time in descending order (most recent results first).
    :return: A list of dictionaries
    """
    with _get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""SELECT * FROM analysis_results ORDER BY log_capture_time DESC""")
        return [dict(row) for row in cur.fetchall()]


def get_results_by_time_range(start: str | None = None, end: str | None = None) -> list[dict[str, str | int]]:
    """
    Queries analysis results within a specified time range.
    :param start: Optional start time (inclusive). Format example: "2025/10/01"
    :param end: Optional end time (inclusive). Format example: "2025/10/31"
    :return: A list of dictionaries
    """

    query = "SELECT * FROM analysis_results"

    conditions = []
    params = []

    if start and start.strip():
        conditions.append("log_capture_time >= ?")
        params.append(start)

    if end and end.strip():
        conditions.append("log_capture_time <= ?")
        params.append(end)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    with _get_connection() as conn:
        conn.row_factory = sqlite3.Row

        cur = conn.cursor()
        cur.execute(query, params)

        return [dict(row) for row in cur.fetchall()]