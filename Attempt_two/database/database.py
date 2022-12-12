import sqlite3


class Database:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.connection = sqlite3.connect(self.filepath)
        self.main_cursor = self.connection.cursor()
        self.main_cursor.execute('PRAGMA JOURNAL_MODE=WAL')
        self.connection.commit()

    def create_pattern(self):
        self.main_cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                filepath TEXT UNIQUE,
                creator TEXT
            )
        ''')
