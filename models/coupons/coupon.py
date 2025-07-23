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
    name = pw.CharField()
    description = pw.CharField()
    is_preset = pw.BooleanField()
    x_position = pw.FloatField(null=True)
    y_position = pw.FloatField(null=True)
    z_position = pw.FloatField(null=True)
    direction = pw.CharField(choices=[(e.value, e.name) for e in DirectionEnum])

    class Meta:
        table_name = 'coupons' 