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
from models.jobs.part import Part
from models.jobs.part_list import PartList

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
    Build, WorkOrder, Job,
    Part, PartList
], safe=True)

database.create_tables([
    Powder, PowderComposition, PowderResults,
    HatchUpSkin, HatchInfill, HatchDownSkin, ContourOnPart, ContourStandard, ContourDown, Edge, Core, Support,
    Setting, Plate, Coupon, CouponComposition, CouponArray,
    Build, WorkOrder, Job,
    Part, PartList
], safe=True)

# Create powders
powder_id = "316L-S312328-1-0"
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
hatch_up_skin = HatchUpSkin.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
hatch_infill = HatchInfill.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
hatch_down_skin = HatchDownSkin.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
contour_on_part = ContourOnPart.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
contour_standard = ContourStandard.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
contour_down = ContourDown.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
edge = Edge.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
core = Core.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
support = Support.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())

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
coupons = []
for i in range(1, 257):
    coupon = Coupon.create(
        name=f"Coupon {i}",
        description=f"Test coupon {i}",
        is_preset=bool(i % 2),
        x_position=round(random.uniform(0, 100), 2),
        y_position=round(random.uniform(0, 100), 2),
        z_position=round(random.uniform(0, 100), 2),
        direction="X"
    )
    # Create composition for all coupons
    CouponComposition.create(
        coupon=coupon,
        H=rand_float(),
        C=rand_float(),
        O=rand_float(),
        Fe=rand_float()
    )
    coupons.append(coupon)

# Create a coupon array with unique coupons
coupon_array = CouponArray.create(
    name="Standard Coupon Array",
    description="Full 256-coupon array for comprehensive testing",
    is_preset=True,
    **{f"coupon_{i+1}": coupons[i] for i in range(256)}
)

# Create additional powders for variety
powder2_id = "Ti64-T123456-2-0"
powder2 = Powder.create(
    id=powder2_id,
    init_date_time=datetime.now(),
    description="Titanium powder batch",
    mat_id="Ti64",
    man_lot="T123456",
    subgroup=2,
    rev=0,
    quantity=75.0
)

powder3_id = "AlSi10Mg-A789012-3-0"
powder3 = Powder.create(
    id=powder3_id,
    init_date_time=datetime.now(),
    description="Aluminum powder batch",
    mat_id="AlSi10Mg",
    man_lot="A789012",
    subgroup=3,
    rev=0,
    quantity=50.0
)

# Create composition and results for powder2 (Titanium)
powder2_comp = PowderComposition.create(
    powder=powder2,
    Fe=rand_float(),
    Cr=rand_float(),
    Ni=rand_float(),
    Mo=rand_float(),
    C=rand_float(),
    Mn=rand_float(),
    Si=rand_float()
)

powder2_results = PowderResults.create(
    powder=powder2,
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

# Create composition and results for powder3 (Aluminum)
powder3_comp = PowderComposition.create(
    powder=powder3,
    Fe=rand_float(),
    Cr=rand_float(),
    Ni=rand_float(),
    Mo=rand_float(),
    C=rand_float(),
    Mn=rand_float(),
    Si=rand_float()
)

powder3_results = PowderResults.create(
    powder=powder3,
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

# Create additional feature settings for setting2
hatch_up_skin2 = HatchUpSkin.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
hatch_infill2 = HatchInfill.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
hatch_down_skin2 = HatchDownSkin.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
contour_on_part2 = ContourOnPart.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
contour_standard2 = ContourStandard.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
contour_down2 = ContourDown.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
edge2 = Edge.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
core2 = Core.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
support2 = Support.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())

# Create additional feature settings for setting3
hatch_up_skin3 = HatchUpSkin.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
hatch_infill3 = HatchInfill.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
hatch_down_skin3 = HatchDownSkin.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
contour_on_part3 = ContourOnPart.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
contour_standard3 = ContourStandard.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
contour_down3 = ContourDown.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
edge3 = Edge.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
core3 = Core.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())
support3 = Support.create(power=rand_float(), scan_speed=rand_float(), layer_thick=rand_float(), hatch_dist=rand_float())

# Create additional settings
setting2 = Setting.create(
    name="High Speed Setting",
    description="High speed production setting",
    is_preset=True,
    hatch_up_skin=hatch_up_skin2,
    hatch_infill=hatch_infill2,
    hatch_down_skin=hatch_down_skin2,
    contour_on_part=contour_on_part2,
    contour_standard=contour_standard2,
    contour_down=contour_down2,
    edge=edge2,
    core=core2,
    support=support2
)

setting3 = Setting.create(
    name="Precision Setting",
    description="High precision setting for critical parts",
    is_preset=True,
    hatch_up_skin=hatch_up_skin3,
    hatch_infill=hatch_infill3,
    hatch_down_skin=hatch_down_skin3,
    contour_on_part=contour_on_part3,
    contour_standard=contour_standard3,
    contour_down=contour_down3,
    edge=edge3,
    core=core3,
    support=support3
)

# Create additional plates
plate2 = Plate.create(
    description="Titanium plate",
    material="Titanium",
    foreign_keys_list=[],
    stamped_heights=[(datetime.now().isoformat(), rand_float()) for _ in range(2)]
)

plate3 = Plate.create(
    description="Aluminum plate",
    material="Aluminum",
    foreign_keys_list=[],
    stamped_heights=[(datetime.now().isoformat(), rand_float()) for _ in range(4)]
)

# Create additional coupon arrays
coupon_array2 = CouponArray.create(
    name="Medium Coupon Array",
    description="128-coupon array for medium-scale testing",
    is_preset=False,
    **{f"coupon_{i+1}": coupons[i % len(coupons)] for i in range(128)}
)

coupon_array3 = CouponArray.create(
    name="Compact Coupon Array",
    description="64-coupon array for quick testing and validation",
    is_preset=True,
    **{f"coupon_{i+1}": coupons[i % len(coupons)] for i in range(64)}
)

# Create builds
build1 = Build.create(
    datetime=datetime.now(),
    name="Test Build 1",
    description="A test build with 316L steel",
    powder_weight_required=rand_float(),
    powder_weight_loaded=rand_float(),
    setting=setting,
    powder=powder,
    plate=plate,
    coupon_array=coupon_array
)

build2 = Build.create(
    datetime=datetime.now(),
    name="Test Build 2",
    description="A test build with Ti64 titanium",
    powder_weight_required=rand_float(),
    powder_weight_loaded=rand_float(),
    setting=setting2,
    powder=powder2,
    plate=plate2,
    coupon_array=coupon_array2
)

build3 = Build.create(
    datetime=datetime.now(),
    name="Test Build 3",
    description="A test build with AlSi10Mg aluminum",
    powder_weight_required=rand_float(),
    powder_weight_loaded=rand_float(),
    setting=setting3,
    powder=powder3,
    plate=plate3,
    coupon_array=coupon_array3
)

# After builds are created, add all build IDs to the first plate's foreign_keys_list
plate.foreign_keys_list = [build1.id, build2.id, build3.id]
plate.save()

# Create Parts
parts = []
for i in range(1, 129):
    part = Part.create(
        name=f"Part{i}",
        description=f"Test part {i}",
        file_path=f"/path/to/part_{i}.stl",
        is_complete=bool(i % 2)
    )
    parts.append(part)

# Create a PartList with only part_1 set
part_list_data = {
    "name": "Standard Part List",
    "description": "A part list for demonstration purposes.",
    "is_preset": True,
    "part_1": parts[0],
    "part_2": parts[1]  # Add a second part for testing
}
part_list = PartList.create(**part_list_data)

# Create work orders
work_order1 = WorkOrder.create(
    name="Work Order 1",
    description="Test work order for steel parts",
    pvid=1,
    part_list=part_list
)

work_order2 = WorkOrder.create(
    name="Work Order 2",
    description="Test work order for titanium parts",
    pvid=2,
    part_list=part_list
)

work_order3 = WorkOrder.create(
    name="Work Order 3",
    description="Test work order for aluminum parts",
    pvid=3,
    part_list=part_list
)

# Create jobs
job1 = Job.create(
    name="Job 1",
    description="Test job for steel build",
    part_list=part_list,
    work_order=work_order1,
    build=build1
)

job2 = Job.create(
    name="Job 2",
    description="Test job for titanium build",
    part_list=part_list,
    work_order=work_order2,
    build=build2
)

job3 = Job.create(
    name="Job 3",
    description="Test job for aluminum build",
    part_list=part_list,
    work_order=work_order3,
    build=build3
)

print("Database seeded with sample data.") 