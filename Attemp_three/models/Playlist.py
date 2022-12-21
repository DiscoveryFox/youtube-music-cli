import json


class Playlist:
    name: str
    songs: list[str]
    creator: str
    id: str

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 songs: list[str] = None,
                 creator: str = None,
                 database_tuple: tuple = None):
        self.name = name
        self.id = id
        self.songs = songs
        self.creator = creator

        if not all([self.name, self.id, self.creator, self.songs]):
            self.id, self.name, self.creator, downloaded, self.songs = database_tuple
            # TODO: Check if there is a nicer way than downloaded maybe like *_ or smth with the
            #  underscore
            self.songs: list[str] = json.loads(self.songs)  # NOQA
