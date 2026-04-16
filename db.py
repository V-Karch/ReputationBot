import sqlite3
from enum import Enum


class ExperienceType(Enum):
    positive = "positive"
    negative = "negative"


class DB:
    def __init__(self, database_name: str):
        self.database_name = database_name
        self.connection = None
        self.cursor = None

    def get_connection(self) -> sqlite3.Connection:
        if self.connection == None:
            connection = sqlite3.connect(self.database_name)
            self.connection = connection
            # If connection is not set
            # Set connection
            # Return connection either way

        return self.connection

    def get_cursor(self) -> sqlite3.Cursor:
        if self.cursor == None:
            connection = self.get_connection()
            cursor = connection.cursor()
            self.cursor = cursor
            # If cursor is not set
            # Set cursor
            # Return cursor either way

        return self.cursor

    def exec_sql(self, sql: str, params: tuple | None = None):
        # Note: this executes raw SQL which may be unsafe
        connection = self.get_connection()
        cursor = self.get_cursor()

        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)

        connection.commit()

    @staticmethod
    def add_entry_to_points_db(
        target_user_id: int,
        author_user_id: int,
        experience_type: ExperienceType,
        reason: str,
    ):
        # Determine point value
        if experience_type == ExperienceType.positive:
            point_value = 1
        else:
            point_value = -1

        sql = """
            INSERT INTO reputation (target_user_id, author_user_id, point_value, reason)
            VALUES (?, ?, ?, ?)
        """

        db = DB("points.db")
        db.exec_sql(sql, (target_user_id, author_user_id, point_value, reason))

    @staticmethod
    def setup_points_db():
        sql = """
            CREATE TABLE IF NOT EXISTS reputation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_user_id INTEGER,
                author_user_id INTEGER,
                point_value INTEGER, -- inferred
                reason TEXT
            )
        """

        db = DB("points.db")
        db.exec_sql(sql)

    @staticmethod
    def get_leaderboard(top_n: int = 10):
        db = DB("points.db")
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT target_user_id, SUM(point_value) as total_points
            FROM reputation
            GROUP BY target_user_id
            ORDER BY total_points DESC
            LIMIT ?
            """,
            (top_n,),
        )
        return cursor.fetchall()

    @staticmethod
    def get_user_rank(user_id: int):
        # This is for the leaderboard.
        db = DB("points.db")
        cursor = db.get_cursor()

        # Check if user has any points
        cursor.execute(
            "SELECT COALESCE(SUM(point_value), 0) FROM reputation WHERE target_user_id = ?",
            (user_id,),
        )
        total = cursor.fetchone()[0]

        if total == 0:
            return 0  # unranked

        # Compute rank
        cursor.execute(
            """
            SELECT COUNT(*) + 1 FROM (
                SELECT target_user_id, SUM(point_value) as total_points
                FROM reputation
                GROUP BY target_user_id
                HAVING total_points > ?
            )
            """,
            (total,),
        )

        row = cursor.fetchone()
        return row[0] if row else 0

    @staticmethod
    def get_unique_traders_count(user_id: int) -> int:
        db = DB("points.db")
        cursor = db.get_cursor()
        cursor.execute(
            """
            SELECT COUNT(DISTINCT author_user_id)
            FROM reputation
            WHERE target_user_id = ?
            AND point_value > 0
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else 0
