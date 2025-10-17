import os
import sqlite3

from Modules.FileProcess.FolderOperator import INSTANCE_PATH

DB_PATH = os.path.join(INSTANCE_PATH, "database.db")
TABLE_AR_FIELDS = [
    "log_capture_time", "estimated_battery_capacity", "last_learned_battery_capacity", "min_learned_battery_capacity",
    "max_learned_battery_capacity", "phone_brand", "nickname", "system_version"
]


def _get_connection() -> sqlite3.Connection:
    """
    Open and return a sqlite3 connection. If database does not exist, it will create it automatically.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_table_ar() -> None:
    """
    Use a series of SQL statements to initialize table called **analysis_results**.
    If table exists, it will be dropped and recreated.
    """
    with _get_connection() as conn:
        cur = conn.cursor()

        init_table = """
        DROP TABLE IF EXISTS analysis_results;
        CREATE TABLE analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_capture_time TEXT NOT NULL,
            estimated_battery_capacity INTEGER NOT NULL,
            last_learned_battery_capacity INTEGER NOT NULL,
            min_learned_battery_capacity INTEGER NOT NULL,
            max_learned_battery_capacity INTEGER NOT NULL,
            phone_brand TEXT NOT NULL COLLATE BINARY,
            nickname TEXT NOT NULL COLLATE BINARY,
            system_version TEXT NOT NULL COLLATE BINARY
        );
        CREATE INDEX IF NOT EXISTS idx_log_capture_time
        ON analysis_results (log_capture_time);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_uni_log
        ON analysis_results (log_capture_time, nickname)
        """

        cur.executescript(init_table)


def save_data_iar(data: dict[str, str | int]) -> int | None:
    """
    Inserts a new row of battery analysis results into the table **analysis_results**.
    :param data: A dictionary containing the following keys: **log_capture_time** (str),
     **estimated_battery_capacity** (int), **last_learned_battery_capacity** (int),
     **min_learned_battery_capacity** (int), **max_learned_battery_capacity** (int), **phone_brand** (str),
     **nickname** (str), **system_version** (str).
    :return: The **id** of the newly inserted record.
    """
    with _get_connection() as conn:
        fields_str = ", ".join(TABLE_AR_FIELDS)
        placeholders_str = ", ".join(["?"] * len(TABLE_AR_FIELDS))

        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO analysis_results ({fields_str}) VALUES ({placeholders_str})",
            [data[field] for field in TABLE_AR_FIELDS]
        )

        return cur.lastrowid


def get_all_results_far() -> list[dict[str, str | int]]:
    """
    Retrieves all data from the table **analysis_results**,
    ordered by capture time in descending order (most recent results first).
    :return: A list of dictionaries
    """
    with _get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""SELECT * FROM analysis_results ORDER BY log_capture_time DESC""")
        return [dict(row) for row in cur.fetchall()]


def get_results_by_time_range_far(start: str | None = None, end: str | None = None) -> list[dict[str, str | int]]:
    """
    Retrieves data within a specified time range from the table **analysis_results**.
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