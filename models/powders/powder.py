"""
Powder model for tracking powder material lots and metadata
"""

import peewee as pw
from models.base import BaseModel

class Powder(BaseModel):
    id = pw.CharField(primary_key=True, unique=True, max_length=128)  # e.g., <matID>-<manLot>-<subgroup>-<rev>
    init_date_time = pw.DateTimeField()  # Required field
    description = pw.CharField(null=True, max_length=255)  # Optional field
    mat_id = pw.CharField(max_length=64)  # Required field
    man_lot = pw.CharField(max_length=64)  # Required field
    subgroup = pw.IntegerField()  # Required field
    rev = pw.IntegerField()  # Required field
    quantity = pw.FloatField(null=True)  # Optional field

    class Meta:
        table_name = 'powders' 