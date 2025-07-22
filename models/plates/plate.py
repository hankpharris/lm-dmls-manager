import peewee as pw

class Plate(pw.Model):
    id = pw.AutoField()
    description = pw.CharField(null=True)
    material = pw.CharField()
    # foreign_keys_list will store a list of related foreign keys (to be defined and referenced later)
    foreign_keys_list = pw.JSONField(null=True)  # TODO: This will store a list of related foreign keys (integers)
    stamped_heights = pw.JSONField(null=True)  # List of (datetime, float) tuples 