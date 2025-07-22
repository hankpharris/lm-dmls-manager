import peewee as pw
from enum import Enum

class DirectionEnum(str, Enum):
    X = "X"
    Y = "Y"
    Z = "Z"
    XY = "XY"
    YZ = "YZ"
    ZX = "ZX"
    OTHER = "OTHER"

class Coupon(pw.Model):
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