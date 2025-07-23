from playhouse.sqlite_ext import JSONField
import peewee as pw

class WorkOrder(pw.Model):
    id = pw.AutoField()
    name = pw.CharField()
    description = pw.CharField()
    pvid = pw.IntegerField()
    parts = JSONField(null=True)  # List of (part_model, part_count) tuples (string, int)
    parent = pw.ForeignKeyField('self', null=True, backref='children')  # Self-referential FK

    class Meta:
        table_name = 'work_orders' 