import peewee as pw
from models.base import BaseModel
from models.settings.feature_settings import (
    HatchUpSkin, HatchInfill, HatchDownSkin, ContourOnPart, ContourStandard, ContourDown, Edge, Core, Support
)

class Setting(BaseModel):
    id = pw.AutoField()  # Auto-incrementing primary key
    name = pw.CharField()
    description = pw.CharField()
    is_preset = pw.BooleanField()
    hatch_up_skin = pw.ForeignKeyField(HatchUpSkin, backref='setting')
    hatch_infill = pw.ForeignKeyField(HatchInfill, backref='setting')
    hatch_down_skin = pw.ForeignKeyField(HatchDownSkin, backref='setting')
    contour_on_part = pw.ForeignKeyField(ContourOnPart, backref='setting')
    contour_standard = pw.ForeignKeyField(ContourStandard, backref='setting')
    contour_down = pw.ForeignKeyField(ContourDown, backref='setting')
    edge = pw.ForeignKeyField(Edge, backref='setting')
    core = pw.ForeignKeyField(Core, backref='setting')
    support = pw.ForeignKeyField(Support, backref='setting')

    class Meta:
        table_name = 'settings' 