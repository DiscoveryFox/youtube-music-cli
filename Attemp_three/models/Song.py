class Song:
    name: str
    filepath: str
    creator: str
    id: str

    def __init__(self, id: str, name: str, filepath: str, creator: str):
        self.id = id
        self.name = name
        self.filepath = filepath
        self.creator = creator

    def __str__(self):
        return f'Song {self.name} from {self.creator} with Id: {self.id} with path:' \
               f' {self.filepath}'
