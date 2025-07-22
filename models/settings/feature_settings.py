import peewee as pw

class BaseFeatureSetting(pw.Model):
    name = pw.CharField(null=True)
    description = pw.CharField(null=True)
    is_preset = pw.BooleanField(null=True)
    power = pw.FloatField(null=True)
    scan_speed = pw.FloatField(null=True)
    layer_thick = pw.FloatField(null=True)
    hatch_dist = pw.FloatField(null=True)
    class Meta:
        abstract = True

class HatchUpSkin(BaseFeatureSetting): pass
class HatchInfill(BaseFeatureSetting): pass
class HatchDownSkin(BaseFeatureSetting): pass
class ContourOnPart(BaseFeatureSetting): pass
class ContourStandard(BaseFeatureSetting): pass
class ContourDown(BaseFeatureSetting): pass
class Edge(BaseFeatureSetting): pass
class Core(BaseFeatureSetting): pass
class Support(BaseFeatureSetting): pass 