import peewee as pw
from models.base import BaseModel

class Part(BaseModel):
    id = pw.AutoField()
    name = pw.CharField(null=True)
    description = pw.CharField(null=True)
    file_path = pw.CharField(null=True)
    is_complete = pw.BooleanField(default=False)

    class Meta:
        table_name = 'parts' 