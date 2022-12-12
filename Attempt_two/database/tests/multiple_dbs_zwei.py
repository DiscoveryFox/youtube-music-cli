import sys

sys.path.append('..')
import database  # NOQA

db: database.Database = database.Database('../songs.db')




