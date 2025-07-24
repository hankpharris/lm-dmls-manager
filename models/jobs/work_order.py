import peewee as pw
from models.base import BaseModel
from models.jobs.part_list import PartList

class WorkOrder(BaseModel):
    id = pw.AutoField()
    name = pw.CharField()
    description = pw.CharField()
    pvid = pw.IntegerField()
    part_list = pw.ForeignKeyField(PartList, null=True, backref='work_orders')

    class Meta:
        table_name = 'work_orders' 