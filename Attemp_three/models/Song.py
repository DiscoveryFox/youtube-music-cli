class Song:
    id: str
    name: str
    filepath: str
    creator: str

    def __init__(self,
                 id: str = None,
                 name: str = None,
                 filepath: str = None,
                 creator: str = None,
                 database_tuple: tuple = None):
        self.id = id
        self.name = name
        self.filepath = filepath
        self.creator = creator

        if not all([self.id, self.name, self.filepath, self.creator]):
            self.id, self.name, self.filepath, self.creator, _ = database_tuple

    def __str__(self):
        return f'Song {self.name} from {self.creator} with Id: {self.id} with path:' \
               f' {self.filepath}'
