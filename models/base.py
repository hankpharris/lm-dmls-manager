import peewee as pw
from database.connection import database
 
class BaseModel(pw.Model):
    class Meta:
        database = database 