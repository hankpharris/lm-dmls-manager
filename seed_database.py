import peewee as pw
from datetime import datetime
import random

from database.connection import database, init_database

# Import all models
from models.powders.powder import Powder
from models.powders.powder_composition import PowderComposition
from models.powders.powder_results import PowderResults
from models.settings.setting import Setting
from models.settings.feature_settings import (
    HatchUpSkin, HatchInfill, HatchDownSkin, ContourOnPart, ContourStandard, ContourDown, Edge, Core, Support
)
from models.plates.plate import Plate
from models.coupons.coupon import Coupon
from models.coupons.coupon_composition import CouponComposition
from models.coupons.coupon_array import CouponArray
from models.jobs.job import Job
from models.jobs.work_order import WorkOrder
from models.builds.build import Build

# Helper for random nullable float
rand_float = lambda: random.choice([round(random.uniform(0, 100), 2), None])
rand_int = lambda: random.choice([random.randint(1, 100), None])
rand_str = lambda: random.choice([f"Sample-{random.randint(1, 1000)}", None])

# Initialize and connect to the database
init_database()

# Drop all tables and recreate them for clean seeding
database.drop_tables([
    Powder, PowderComposition, PowderResults,
    HatchUpSkin, HatchInfill, HatchDownSkin, ContourOnPart, ContourStandard, ContourDown, Edge, Core, Support,
    Setting, Plate, Coupon, CouponComposition, CouponArray,
    Build, WorkOrder, Job
], safe=True)

database.create_tables([
    Powder, PowderComposition, PowderResults,
    HatchUpSkin, HatchInfill, HatchDownSkin, ContourOnPart, ContourStandard, ContourDown, Edge, Core, Support,
    Setting, Plate, Coupon, CouponComposition, CouponArray,
    Build, WorkOrder, Job
], safe=True)

# Create powders
powder_id = f"316L-[S312328]-1-0-{int(datetime.now().timestamp())}"
powder = Powder.create(
    id=powder_id,
    init_date_time=datetime.now(),
    description="Test powder batch",
    mat_id="316L",
    man_lot="S312328",
    subgroup=1,
    rev=0,
    quantity=100.0
)

powder_comp = PowderComposition.create(
    powder=powder,
    Fe=rand_float(),
    Cr=rand_float(),
    Ni=rand_float(),
    Mo=rand_float(),
    C=rand_float(),
    Mn=rand_float(),
    Si=rand_float()
)

powder_results = PowderResults.create(
    powder=powder,
    water_content=rand_float(),
    skeletal_density=rand_float(),
    sphericity=rand_float(),
    symmetry=rand_float(),
    aspect_ratio=rand_float(),
    d10=rand_int(),
    d50=rand_int(),
    d90=rand_int(),
    xcmin10=rand_int(),
    xcmin50=rand_int(),
    xcmin90=rand_int(),
    perc_wt_gt_53=rand_float(),
    perc_wt_gt_63=rand_float(),
    apparent_dens=rand_float()
)

# Create feature settings
hatch_up_skin = HatchUpSkin.create(name="HatchUpSkin", power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float(), is_preset=True)
hatch_infill = HatchInfill.create(name="HatchInfill", power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float(), is_preset=True)
hatch_down_skin = HatchDownSkin.create(name="HatchDownSkin", power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float(), is_preset=True)
contour_on_part = ContourOnPart.create(name="ContourOnPart", power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float(), is_preset=True)
contour_standard = ContourStandard.create(name="ContourStandard", power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float(), is_preset=True)
contour_down = ContourDown.create(name="ContourDown", power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float(), is_preset=True)
edge = Edge.create(name="Edge", power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float(), is_preset=True)
core = Core.create(name="Core", power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float(), is_preset=True)
support = Support.create(name="Support", power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float(), is_preset=True)

setting = Setting.create(
    name="Default Setting",
    description="A default setting preset",
    is_preset=True,
    hatch_up_skin=hatch_up_skin,
    hatch_infill=hatch_infill,
    hatch_down_skin=hatch_down_skin,
    contour_on_part=contour_on_part,
    contour_standard=contour_standard,
    contour_down=contour_down,
    edge=edge,
    core=core,
    support=support
)

# Create plate
plate = Plate.create(
    description="Test plate",
    material="Steel",
    foreign_keys_list=[],
    stamped_heights=[(datetime.now().isoformat(), rand_float()) for _ in range(3)]
)

# Create coupons and coupon compositions
coupon_compositions = []
coupons = []
for i in range(1, 6):
    comp = CouponComposition.create(
        H=rand_float(),
        C=rand_float(),
        O=rand_float(),
        Fe=rand_float()
    )
    coupon = Coupon.create(
        name=f"Coupon {i}",
        description=f"Test coupon {i}",
        is_preset=bool(i % 2),
        x_position=rand_float(),
        y_position=rand_float(),
        z_position=rand_float(),
        direction="X",
        coupon_composition=comp
    )
    coupon_compositions.append(comp)
    coupons.append(coupon)

# Create a coupon array
coupon_array = CouponArray.create(
    is_preset=True,
    **{f"coupon_{i+1}": coupons[i % len(coupons)] for i in range(256)}
)

# Create a build
build = Build.create(
    datetime=datetime.now(),
    name="Test Build",
    description="A test build",
    powder_weight_required=rand_float(),
    powder_weight_loaded=rand_float(),
    setting=setting,
    powder=powder,
    plate=plate,
    coupon_array=coupon_array
)

# Create a work order
work_order = WorkOrder.create(
    name="Work Order 1",
    description="Test work order",
    pvid=1,
    parts=[("PartA", 10), ("PartB", 5)],
    parent=None
)

# Create a job
job = Job.create(
    name="Job 1",
    description="Test job",
    parts=[("PartA", 10), ("PartB", 5)],
    work_order=work_order,
    build=build
)

print("Database seeded with sample data.") 