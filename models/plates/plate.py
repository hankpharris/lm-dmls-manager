from playhouse.sqlite_ext import JSONField
import peewee as pw
from models.base import BaseModel

class Plate(BaseModel):
    id = pw.AutoField()
    description = pw.CharField(null=True)
    material = pw.CharField()
    # foreign_keys_list will store a list of related foreign keys (to be defined and referenced later)
    foreign_keys_list = JSONField(null=True)  # TODO: This will store a list of related foreign keys (integers)
    stamped_heights = JSONField(null=True)  # List of (datetime, float) tuples

    class Meta:
        table_name = 'plates' 