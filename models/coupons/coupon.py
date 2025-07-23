import peewee as pw
from enum import Enum
from models.base import BaseModel

class DirectionEnum(str, Enum):
    X = "X"
    Y = "Y"
    Z = "Z"
    XY = "XY"
    YZ = "YZ"
    ZX = "ZX"
    OTHER = "OTHER"

class Coupon(BaseModel):
    id = pw.AutoField()
    name = pw.CharField(null=True)  # Optional field
    description = pw.CharField(null=True)  # Optional field
    is_preset = pw.BooleanField()  # Required field
    x_position = pw.FloatField()  # Required field
    y_position = pw.FloatField()  # Required field
    z_position = pw.FloatField()  # Required field
    direction = pw.CharField(choices=[(e.value, e.name) for e in DirectionEnum])  # Required field

    class Meta:
        table_name = 'coupons' 