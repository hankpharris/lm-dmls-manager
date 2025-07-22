"""
Powder model for tracking powder material lots and metadata
"""

import peewee as pw

class Powder(pw.Model):
    id = pw.CharField(primary_key=True, unique=True, max_length=128)  # e.g., <matID>-<manLot>-<subgroup>-<rev>
    init_date_time = pw.DateTimeField(null=True)
    description = pw.CharField(null=True, max_length=255)
    mat_id = pw.CharField(null=True, max_length=64)
    man_lot = pw.CharField(null=True, max_length=64)
    subgroup = pw.IntegerField(null=True)
    rev = pw.IntegerField(null=True)
    quantity = pw.FloatField(null=True)

    class Meta:
        table_name = 'powders' 