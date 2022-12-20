import sqlite3
from models.Playlist import Playlist
from models.Song import Song


class Database:
    class Connection:
        def __init__(self, database_path: str):
            self.connection = sqlite3.connect(database_path, check_same_thread=False)
            self.cursor = self.connection.cursor()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.cursor.close()
            self.connection.close()

    def __init__(self, database_path: str):
        self.database_path = database_path
        self.connection = sqlite3.connect(database_path, check_same_thread=False)
        self.main_cursor = self.connection.cursor()
        self.main_cursor.execute('PRAGMA JOURNAL_MODE=WAL')
        self.connection.commit()
        self.create_default_layout()
        self.main_cursor.close()
        self.connection.close()

    def get_connection(self):
        with self.Connection(database_path) as conn:
            ...

    def in_database(self, video_id: str):
        ...

    def register_song(self, song: Song):
        ...

    def register_playlist(self, playlist: Playlist):
        ...

    def confirm_song(self, id: str):
        ...

    def confirm_playlist(self, id: str):
        ...

    def create_default_layout(self):
        with self.Connection(self.database_path) as conn:
            conn.cursor.execute('''
CREATE TABLE IF NOT EXISTS Playlists (
    PlaylistID TEXT PRIMARY KEY NOT NULL,
    Name TEXT NOT NULL,
    Creator TEXT NOT NULL,
    Downloaded BOOLEAN NOT NULL,
    Songs TEXT NOT NULL
);
            ''')
            conn.cursor.execute('''
CREATE TABLE IF NOT EXISTS Songs (
    VideoID TEXT PRIMARY KEY NOT NULL,
    Name TEXT NOT NULL,
    Filepath TEXT UNIQUE NOT NULL,
    Creator TEXT NOT NULL,
    Downloaded BOOLEAN NOT NULL
);
            ''')
            conn.connection.commit()



