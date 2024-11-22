#!/usr/bin/env python3

import sqlite3


class SelfDB:
    def __init__(self, db_name: str):
        """Initialize and connect to the SQLite database."""
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        print(f"Connected to database '{db_name}'")

    def create_table(self, table_name: str, columns: dict):
        """Create a table in the database.

        Parameters:
            table_name (str): Name of the table.
            columns (dict): Dictionary with column names as keys and data types as values.
        """
        columns_def = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        sql_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        self.cursor.execute(sql_query)
        print(f"Table '{table_name}' created or already exists.")

    def insert_data(self, table_name: str, data: dict):
        """Insert a row of data into a specified table.

        Parameters:
            table_name (str): Name of the table.
            data (dict): Dictionary with column names as keys and row data as values.
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql_query, tuple(data.values()))
        self.connection.commit()
        print(f"Inserted data into '{table_name}': {data}")

    def read_data(self, table_name: str, columns="*", where_clause=""):
        """Read data from a specified table with an optional where clause.

        Parameters:
            table_name (str): Name of the table.
            columns (str or list): Columns to retrieve. Default is '*'.
            where_clause (str): Optional SQL where clause.

        Returns:
            list of tuple: Retrieved data rows.
        """
        columns = ", ".join(columns) if isinstance(columns, (list, tuple)) else columns
        sql_query = f"SELECT {columns} FROM {table_name} {where_clause}"
        self.cursor.execute(sql_query)
        rows = self.cursor.fetchall()
        print(f"Retrieved data from '{table_name}': {rows}")
        return rows

    def close(self):
        """Close the database connection."""
        self.connection.close()
        print("Database connection closed.")


# Example Usage
if __name__ == "__main__":
    db = SelfDB("example.db")
    db.create_table(
        "users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"}
    )
    db.insert_data("users", {"name": "Alice", "age": 30})
    data = db.read_data("users")
    db.close()
