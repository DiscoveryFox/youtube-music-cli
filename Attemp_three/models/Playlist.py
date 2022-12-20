class Playlist:
    name: str
    songs: list[str]
    creator: str
    id: str

    def __init__(self, id: str, name: str, songs: list[str], creator: str):
        self.name = name
        self.id = id
        self.songs = songs
        self.creator = creator
