import sqlite3

from .connect import BaseStorage


class UploadRecord(BaseStorage):
    def __init__(self) -> None:
        super().__init__()
        self.table_name = ["file_abs_path", "size"]

    def init_table(self) -> None:
        """
        Initialize table called **upload_record**.
        If table exists, its data will be overwritten (drop & create).
        """
        init_statement = """
                         DROP TABLE IF EXISTS upload_record;
                         CREATE TABLE upload_record
                         (
                             file_abs_path TEXT PRIMARY KEY COLLATE BINARY,
                             size          INTEGER NOT NULL
                         );
                         """

        with self.conn as c:
            cur = c.cursor()
            cur.executescript(init_statement)

    def save_data(self, data: list[dict[str, str | int]]) -> int:
        """
        Insert some metadata of uploaded files into table called **upload_record**.

        Parameters
        ----------
        data: list[dict[str, str | int]]
            A list of dictionaries containing:

            - file_abs_path : str
            - size : int

        Returns
        -------
        int
            The number of rows inserted successfully.
        """
        fields_str = ", ".join(self.table_name)
        placeholders_str = ", ".join(["?"] * len(self.table_name))

        counts = 0

        with self.conn as c:
            cur = c.cursor()
            cur.executemany(
                f"INSERT INTO upload_record ({fields_str}) VALUES ({placeholders_str})",
                [[item[fields] for fields in self.table_name] for item in data]
            )

            counts = cur.rowcount

        return counts

    def get_all_results(self) -> list[dict[str, str | int]] | None:
        results = None
        with self.conn as c:
            c.row_factory = sqlite3.Row
            cur = c.cursor()
            cur.execute("SELECT * FROM upload_record ORDER BY file_abs_path DESC")
            results = [dict(row) for row in cur.fetchall()]

        return results
