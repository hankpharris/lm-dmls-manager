import peewee as pw
from models.settings.setting import Setting
from models.powders.powder import Powder
from models.plates.plate import Plate
from models.coupons.coupon_array import CouponArray

class Build(pw.Model):
    id = pw.AutoField()
    datetime = pw.DateTimeField()
    name = pw.CharField()
    description = pw.CharField()
    powder_weight_required = pw.FloatField()
    powder_weight_loaded = pw.FloatField()
    setting = pw.ForeignKeyField(Setting, backref='builds')
    powder = pw.ForeignKeyField(Powder, backref='builds')
    plate = pw.ForeignKeyField(Plate, backref='builds')
    coupon_array = pw.ForeignKeyField(CouponArray, backref='builds')

    class Meta:
        table_name = 'builds' 