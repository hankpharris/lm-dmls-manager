from playhouse.sqlite_ext import JSONField
import peewee as pw
from models.base import BaseModel
from models.jobs.work_order import WorkOrder
from models.builds.build import Build

class Job(BaseModel):
    id = pw.AutoField()
    name = pw.CharField()
    description = pw.CharField()
    parts = JSONField(null=True)  # List of (part_model, part_count) tuples (string, int)
    work_order = pw.ForeignKeyField(WorkOrder, backref='jobs')
    build = pw.ForeignKeyField(Build, backref='jobs')

    class Meta:
        table_name = 'jobs' 