import sqlite3
import json

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

    def in_database(self, song_id: str) -> bool:
        with self.Connection(self.database_path) as db:
            db.cursor.execute('SELECT * FROM Songs WHERE SongID = ? UNION SELECT * FROM Playlists '
                              'WHERE PlaylistID = ?',
                              (song_id, song_id))
            if not db.cursor.fetchall():
                return False
            else:
                return True

    def register_song(self, song: Song):
        with self.Connection(self.database_path) as db:
            db.cursor.execute('INSERT INTO songs (SongID, Name, Filepath, Creator, Downloaded) '
                              'VALUES (?, ?, ?, ?, ?)',
                              (song.id, song.name, song.filepath, song.creator, False)
                              )
            db.connection.commit()

    def register_playlist(self, playlist: Playlist):
        with self.Connection(self.database_path) as db:
            db.cursor.execute('INSERT INTO Playlists (PlaylistID, Name, Creator, Downloaded, '
                              'Songs) '
                              'VALUES (?, ?, ?, ?, ?)',
                              (playlist.id, playlist.name, playlist.creator, False,
                               json.dumps(playlist.songs))
                              )
            db.connection.commit()

    def confirm_song(self, id: str):
        with self.Connection(self.database_path) as db:
            db.cursor.execute('UPDATE songs SET Downloaded = ? WHERE SongID = ?', (True, id))
            db.connection.commit()

    def confirm_playlist(self, id: str):
        with self.Connection(self.database_path) as db:
            db.cursor.execute('UPDATE playlists SET Downloaded = ? WHERE PlaylistID = ?',
                              (True, id))
            db.connection.commit()

    def list_playlists(self):
        with self.Connection(self.database_path) as db:
            db.cursor.execute('SELECT * FROM playlists')
            return [Playlist(database_tuple=playlist) for playlist in db.cursor.fetchall()]

    def list_songs(self):
        with self.Connection(self.database_path) as db:
            db.cursor.execute('SELECT * FROM songs')
            return [Song(database_tuple=song) for song in db.cursor.fetchall()]

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
    SongID TEXT PRIMARY KEY NOT NULL,
    Name TEXT NOT NULL,
    Filepath TEXT UNIQUE NOT NULL,
    Creator TEXT NOT NULL,
    Downloaded BOOLEAN NOT NULL
);
            ''')
            conn.connection.commit()


if __name__ == '__main__':
    x = Database(r'C:\Users\Flinn\Documents\youtube-music-cli\Attempt_one\cache\songs.db')
    print(x.list_playlists())
