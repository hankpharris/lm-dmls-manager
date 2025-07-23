import os
import peewee as pw
from playhouse.sqlite_ext import SqliteExtDatabase

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dmls_powder.db')

database = SqliteExtDatabase(DB_PATH)

def init_database():
    if database.is_closed():
        database.connect() 