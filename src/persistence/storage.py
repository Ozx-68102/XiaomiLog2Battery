import sqlite3

from src.config import DB_PATH, TABLE_FIELDS


def _get_connection() -> sqlite3.Connection:
    """
    Open and return a sqlite3 connection. If database does not exist, it will create it automatically.

    Returns
    -------
    sqlite3.Connection
        a sqlite3 connection.

    """
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_table() -> None:
    """
    Use a series of SQL statements to initialize table called **analysis_results**.
    If table exists, it will be dropped and recreated.
    """
    with _get_connection() as c:
        cur = c.cursor()

        init_statement = """
                         DROP TABLE IF EXISTS analysis_results;
                         CREATE TABLE analysis_results
                         (
                             id                            INTEGER PRIMARY KEY AUTOINCREMENT,
                             log_capture_time              TEXT    NOT NULL,
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
                             ON analysis_results (log_capture_time, nickname) \
                         """

        cur.executescript(init_statement)


def save_data(data: list[dict[str, str | int]]) -> int:
    """
    Insert rows of battery analysis results into the table **analysis_results**.
    Parameters
    ----------
    data: list[dict[str, str | int]]
        A list of dictionaries containing keys of `TABLE_FIELDS`.

        - log_capture_time : str
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

    fields_str = ", ".join(TABLE_FIELDS)
    placeholders_str = ", ".join(["?"] * len(TABLE_FIELDS))

    counts = 0

    with _get_connection() as c:
        cur = c.cursor()
        cur.executemany(
            f"INSERT INTO analysis_results ({fields_str}) VALUES ({placeholders_str})",
            [[item[fields] for fields in TABLE_FIELDS] for item in data]
        )

        counts = cur.rowcount

    return counts


def get_all_results() -> list[dict[str, str | int]] | None:
    results = None
    with _get_connection() as c:
        c.row_factory = sqlite3.Row
        cur = c.cursor()
        cur.execute("SELECT * FROM analysis_results ORDER BY log_capture_time DESC")
        results = [dict(row) for row in cur.fetchall()]

    return results if results else None
