import peewee as pw
from models.print_settings.feature_settings import (
    HatchUpSkin, HatchInfill, HatchDownSkin, ContourOnPart, ContourStandard, ContourDown, Edge, Core, Support
)

class Settings(pw.Model):
    id = pw.AutoField()  # Auto-incrementing primary key
    name = pw.CharField()
    description = pw.CharField()
    is_preset = pw.BooleanField()
    hatch_up_skin = pw.ForeignKeyField(HatchUpSkin, backref='settings')
    hatch_infill = pw.ForeignKeyField(HatchInfill, backref='settings')
    hatch_down_skin = pw.ForeignKeyField(HatchDownSkin, backref='settings')
    contour_on_part = pw.ForeignKeyField(ContourOnPart, backref='settings')
    contour_standard = pw.ForeignKeyField(ContourStandard, backref='settings')
    contour_down = pw.ForeignKeyField(ContourDown, backref='settings')
    edge = pw.ForeignKeyField(Edge, backref='settings')
    core = pw.ForeignKeyField(Core, backref='settings')
    support = pw.ForeignKeyField(Support, backref='settings') 