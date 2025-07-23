import peewee as pw
from database.connection import database
from models.base import BaseModel

class BaseFeatureSetting(BaseModel):
    power = pw.FloatField(null=True)
    scan_speed = pw.FloatField(null=True)
    layer_thick = pw.FloatField(null=True)
    hatch_dist = pw.FloatField(null=True)
    class Meta:
        abstract = True

class HatchUpSkin(BaseFeatureSetting):
    class Meta:
        table_name = 'hatch_up_skins'

class HatchInfill(BaseFeatureSetting):
    class Meta:
        table_name = 'hatch_infills'

class HatchDownSkin(BaseFeatureSetting):
    class Meta:
        table_name = 'hatch_down_skins'

class ContourOnPart(BaseFeatureSetting):
    class Meta:
        table_name = 'contour_on_parts'

class ContourStandard(BaseFeatureSetting):
    class Meta:
        table_name = 'contour_standards'

class ContourDown(BaseFeatureSetting):
    class Meta:
        table_name = 'contour_downs'

class Edge(BaseFeatureSetting):
    class Meta:
        table_name = 'edges'

class Core(BaseFeatureSetting):
    class Meta:
        table_name = 'cores'

class Support(BaseFeatureSetting):
    class Meta:
        table_name = 'supports' 