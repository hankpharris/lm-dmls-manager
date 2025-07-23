"""
PowderResults model for storing various powder test results
"""

import peewee as pw
from models.base import BaseModel
from models.powders.powder import Powder

class PowderResults(BaseModel):
    powder = pw.ForeignKeyField(Powder, primary_key=True, backref='results', on_delete='CASCADE')
    water_content = pw.FloatField(null=True)
    skeletal_density = pw.FloatField(null=True)
    sphericity = pw.FloatField(null=True)
    symmetry = pw.FloatField(null=True)
    aspect_ratio = pw.FloatField(null=True)
    d10 = pw.IntegerField(null=True)
    d50 = pw.IntegerField(null=True)
    d90 = pw.IntegerField(null=True)
    xcmin10 = pw.IntegerField(null=True)
    xcmin50 = pw.IntegerField(null=True)
    xcmin90 = pw.IntegerField(null=True)
    perc_wt_gt_53 = pw.FloatField(null=True)
    perc_wt_gt_63 = pw.FloatField(null=True)
    apparent_dens = pw.FloatField(null=True)

    class Meta:
        table_name = 'powder_results' 