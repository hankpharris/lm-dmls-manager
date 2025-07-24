from playhouse.sqlite_ext import JSONField
import peewee as pw
from models.base import BaseModel
from models.jobs.work_order import WorkOrder
from models.builds.build import Build
from models.jobs.part_list import PartList

class Job(BaseModel):
    id = pw.AutoField()
    name = pw.CharField()
    description = pw.CharField()
    part_list = pw.ForeignKeyField(PartList, null=True, backref='jobs')
    work_order = pw.ForeignKeyField(WorkOrder, null=False, backref='jobs')
    build = pw.ForeignKeyField(Build, backref='jobs')

    class Meta:
        table_name = 'jobs' 