import sqlite3


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
