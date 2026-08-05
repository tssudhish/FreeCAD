import os
import FreeCAD as App
import Part

print("Executing Complete Airbus A380 1:80 Scale Assembly Generation...")

doc_name = "Airbus_A380_1to80"
if doc_name in App.listDocuments():
    App.closeDocument(doc_name)
doc = App.newDocument(doc_name)

# SPECIFICATION CONSTANTS (1:80 Scale in mm)
OVERALL_LENGTH = 909.00         # 72.72 m full scale
FUSELAGE_ONLY_LENGTH = 880.00   # 70.40 m full scale
MAX_EXTERIOR_HEIGHT = 105.10    # 8.41 m full scale
MAIN_DECK_WIDTH = 89.25         # 7.14 m full scale
UPPER_DECK_WIDTH = 73.25        # 5.86 m full scale
DECK_SEPARATION = 36.25         # 2.90 m full scale
TOTAL_AIRCRAFT_HEIGHT = 301.125 # 24.09 m full scale
WINGSPAN = 996.88               # 79.75 m full scale
Z_GROUND = -60.20

# 1. FUSELAGE OVOID (DOUBLE-BUBBLE) CROSS-SECTION GENERATOR
def make_ovoid_wire(x, total_height, main_width, upper_width, z_center):
    h = max(total_height, 0.5)
    w_m = max(main_width / 2.0, 0.25)
    w_u = max(upper_width / 2.0, 0.25)
    d_sep = DECK_SEPARATION * min(h / MAX_EXTERIOR_HEIGHT, 1.0)
    pts_norm = [
        ( 0.0,            z_center + h * 0.50),
        ( w_u * 0.75,     z_center + h * 0.42),
        ( w_u,            z_center + d_sep * 0.5),
        ( (w_m+w_u)*0.48, z_center),
        ( w_m,            z_center - d_sep * 0.5),
        ( w_m * 0.75,     z_center - h * 0.42),
        ( 0.0,            z_center - h * 0.50),
        (-w_m * 0.75,     z_center - h * 0.42),
        (-w_m,            z_center - d_sep * 0.5),
        (-(w_m+w_u)*0.48, z_center),
        (-w_u,            z_center + d_sep * 0.5),
        (-w_u * 0.75,     z_center + h * 0.42)
    ]
    vecs = [App.Vector(x, py, pz) for py, pz in pts_norm]
    bspline = Part.BSplineCurve()
    bspline.interpolate(vecs, True)
    return Part.Wire([bspline.toShape()])

# 2. AIRFOIL GENERATORS (TRANSONIC / NACA AIRFOILS)
def make_airfoil_xy(x_lead, y, z_center, chord, thickness_factor=0.11):
    pts_norm = [
        (0.000, 0.000), (0.025, 0.30), (0.075, 0.46), (0.150, 0.54),
        (0.250, 0.56), (0.400, 0.50), (0.600, 0.36), (0.800, 0.18),
        (1.000, 0.02), (1.000,-0.02), (0.800,-0.10), (0.600,-0.20),
        (0.400,-0.30), (0.250,-0.34), (0.150,-0.32), (0.075,-0.24),
        (0.025,-0.15), (0.000, 0.000)
    ]
    vecs = [App.Vector(x_lead + xn * chord, y, z_center + zn * chord * thickness_factor) for xn, zn in pts_norm]
    bspline = Part.BSplineCurve()
    bspline.interpolate(vecs, False)
    return Part.Wire([bspline.toShape()])

def make_airfoil_xz(x_lead, y_off, z_lead, chord, thickness_factor=0.10):
    pts_norm = [
        (0.000, 0.000), (0.025, 0.30), (0.075, 0.45), (0.150, 0.52),
        (0.250, 0.54), (0.400, 0.48), (0.600, 0.35), (0.800, 0.18),
        (1.000, 0.02), (1.000,-0.02), (0.800,-0.18), (0.600,-0.35),
        (0.400,-0.48), (0.250,-0.54), (0.150,-0.52), (0.075,-0.45),
        (0.025,-0.30), (0.000, 0.000)
    ]
    vecs = [App.Vector(x_lead + xn * chord, y_off + zn * chord * thickness_factor, z_lead) for xn, zn in pts_norm]
    bspline = Part.BSplineCurve()
    bspline.interpolate(vecs, False)
    return Part.Wire([bspline.toShape()])

# 3. FUSELAGE LOFTING & BELLY FAIRING
fuse_specs = [
    (0.0,    2.0,   2.0,   1.8, -10.0),
    (12.0,  20.0,  18.0,  15.0,  -8.0),
    (35.0,  45.0,  40.0,  34.0,  -4.0),
    (70.0,  75.0,  68.0,  56.0,  -1.0),
    (110.0, 98.0,  84.0,  68.0,   0.0),
    (150.0, MAX_EXTERIOR_HEIGHT, MAIN_DECK_WIDTH, UPPER_DECK_WIDTH, 0.0),
    (300.0, MAX_EXTERIOR_HEIGHT, MAIN_DECK_WIDTH, UPPER_DECK_WIDTH, 0.0),
    (560.0, MAX_EXTERIOR_HEIGHT, MAIN_DECK_WIDTH, UPPER_DECK_WIDTH, 0.0),
    (640.0, 96.0,  80.0,  64.0,   3.0),
    (720.0, 72.0,  56.0,  44.0,   8.0),
    (800.0, 44.0,  32.0,  24.0,  14.0),
    (FUSELAGE_ONLY_LENGTH, 22.0, 16.0, 12.0, 18.0),
    (OVERALL_LENGTH, 3.0, 2.0, 1.5, 22.0)
]
fuselage = Part.makeLoft([make_ovoid_wire(x, h, wm, wu, zc) for x, h, wm, wu, zc in fuse_specs], True)

belly_specs = [
    (260.0,  12.0, 10.0, -14.0),
    (300.0,  60.0, 24.0, -18.0),
    (380.0,  96.0, 30.0, -22.0),
    (480.0,  88.0, 26.0, -20.0),
    (550.0,  45.0, 16.0, -16.0),
    (590.0,  12.0,  8.0, -13.0)
]
belly_wires = []
for x_b, w_b, h_b, z_b in belly_specs:
    e = Part.Ellipse()
    e.Center = App.Vector(x_b, 0, z_b)
    e.MajorRadius = max(w_b, h_b) / 2.0
    e.MinorRadius = min(w_b, h_b) / 2.0
    e.Axis = App.Vector(1, 0, 0)
    belly_wires.append(Part.Wire([e.toShape()]))

belly_fairing = Part.makeLoft(belly_wires, True)

# 4. GULL WINGS WITH ORIENTATION CONSISTENCY
# Right wing root (+Y) to tip (+Y)
wing_stations_right = [
    (  0.0,   300.0, -16.0, 230.0, 0.13),
    ( 44.625, 328.0, -14.0, 210.0, 0.12),
    (100.0,   372.0,  -4.0, 182.0, 0.11),
    (156.25,  412.0,   6.0, 160.0, 0.11),
    (287.5,   490.0,  18.0, 114.0, 0.10),
    (480.0,   605.0,  36.0,  43.0, 0.09),
    (498.4,   616.0,  38.5,  35.0, 0.08)
]
r_wing = Part.makeLoft([make_airfoil_xy(x, y, z, c, t) for y, x, z, c, t in wing_stations_right], True)

# Left wing tip (-Y) to root (-Y) using reversed station ordering
l_wing = Part.makeLoft([make_airfoil_xy(x, -y, z, c, t) for y, x, z, c, t in reversed(wing_stations_right)], True)

# 5. DUAL-ENDED WINGTIP FENCES (UPPER & LOWER EXTENSIONS)
def make_dual_wingtip_fence(y_sign):
    y_pos = 498.4 * y_sign
    thickness = 1.5 * y_sign
    z_tip = 38.5
    
    upper_pts = [
        App.Vector(614.0, y_pos, z_tip),
        App.Vector(651.0, y_pos, z_tip),
        App.Vector(646.0, y_pos + 1.2 * y_sign, z_tip + 33.5),
        App.Vector(626.0, y_pos + 1.2 * y_sign, z_tip + 33.5),
        App.Vector(614.0, y_pos, z_tip)
    ]
    face_u = Part.Face(Part.makePolygon(upper_pts))
    solid_u = face_u.extrude(App.Vector(0, thickness, 0))
    
    lower_pts = [
        App.Vector(614.0, y_pos, z_tip),
        App.Vector(651.0, y_pos, z_tip),
        App.Vector(648.0, y_pos - 0.5 * y_sign, z_tip - 16.5),
        App.Vector(620.0, y_pos - 0.5 * y_sign, z_tip - 16.5),
        App.Vector(614.0, y_pos, z_tip)
    ]
    face_l = Part.Face(Part.makePolygon(lower_pts))
    solid_l = face_l.extrude(App.Vector(0, thickness, 0))
    
    return solid_u.fuse(solid_l)

winglet_r = make_dual_wingtip_fence(1)
winglet_l = make_dual_wingtip_fence(-1)

# 6. FLAP TRACK CANOES (3 PER WING UNDERSIDE)
def make_flap_canoe(x_lead, y_pos, z_wing, length, max_diam):
    r = max_diam / 2.0
    x_mid = x_lead + length * 0.4
    x_tail = x_lead + length
    z_in = z_wing + 2.0
    c_specs = [
        (x_lead,        max(r * 0.2, 0.5), z_in),
        (x_mid,         r,                 z_in - r*0.5),
        (x_tail - 8.0,  r * 0.6,           z_in - r*0.3),
        (x_tail,        max(r * 0.1, 0.4), z_in)
    ]
    c_wires = [Part.Wire([Part.makeCircle(rc, App.Vector(xc, y_pos, zc), App.Vector(1, 0, 0))]) for xc, rc, zc in c_specs]
    return Part.makeLoft(c_wires, True)

canoes = [
    make_flap_canoe(430.0,  110.0,  -3.0, 95.0, 12.0),
    make_flap_canoe(500.0,  210.0,   8.0, 80.0, 10.0),
    make_flap_canoe(550.0,  330.0,  22.0, 65.0,  8.0),
    make_flap_canoe(430.0, -110.0,  -3.0, 95.0, 12.0),
    make_flap_canoe(500.0, -210.0,   8.0, 80.0, 10.0),
    make_flap_canoe(550.0, -330.0,  22.0, 65.0,  8.0)
]

# 7. EMPENNAGE (VERTICAL TAILFIN & HORIZONTAL STABILIZERS)
vtail_stations = [
    ( 30.0,   650.0, 0.0, 180.0, 0.10),
    (100.0,   705.0, 0.0, 125.0, 0.09),
    (170.0,   755.0, 0.0,  80.0, 0.08),
    (240.925, 788.0, 0.0,  52.0, 0.07)
]
vtail = Part.makeLoft([make_airfoil_xz(x, y, z, c, t) for z, x, y, c, t in vtail_stations], True)

htail_stations_right = [
    (  0.0, 740.0, 15.0, 110.0, 0.09),
    ( 60.0, 768.0, 18.0,  86.0, 0.08),
    (130.0, 800.0, 22.0,  58.0, 0.08),
    (190.0, 828.0, 25.5,  35.0, 0.07)
]
r_htail = Part.makeLoft([make_airfoil_xy(x, y, z, c, t) for y, x, z, c, t in htail_stations_right], True)
l_htail = Part.makeLoft([make_airfoil_xy(x, -y, z, c, t) for y, x, z, c, t in reversed(htail_stations_right)], True)

# 8. PROPULSION (4 TURBOFAN ENGINES WITH PYLONS & EXHAUST CONES)
def make_engine(x_center, y_pos, z_center, wing_z):
    x_start = x_center - 36.25
    x_end = x_center + 36.25
    r_max = 20.625
    r_fan = 18.44
    nacelle_specs = [
        (x_start,        r_fan),
        (x_start + 12.0, r_max),
        (x_center + 10.0,r_max * 0.95),
        (x_end - 8.0,    r_max * 0.82),
        (x_end,          r_max * 0.75)
    ]
    n_wires = [Part.Wire([Part.makeCircle(r_n, App.Vector(x_n, y_pos, z_center), App.Vector(1, 0, 0))]) for x_n, r_n in nacelle_specs]
    nacelle = Part.makeLoft(n_wires, True)
    
    fan_disk = Part.makeCylinder(r_fan - 1.0, 2.0, App.Vector(x_start + 1.0, y_pos, z_center), App.Vector(1, 0, 0))
    fan_hub = Part.makeCone(4.0, 0.5, 6.0, App.Vector(x_start + 1.0, y_pos, z_center), App.Vector(1, 0, 0))
    exhaust_cone = Part.makeCone(12.0, 1.0, 20.0, App.Vector(x_end - 8.0, y_pos, z_center), App.Vector(1, 0, 0))
    
    pylon_height = wing_z - z_center + 6.0
    pylon_box = Part.makeBox(48.0, 3.5, pylon_height)
    pylon_box.translate(App.Vector(x_start + 10.0, y_pos - 1.75, z_center + r_max - 4.0))
    
    return Part.makeCompound([nacelle, fan_disk, fan_hub, exhaust_cone, pylon_box])

engines = [
    make_engine(370.0,  156.25, -22.0,   6.0),
    make_engine(370.0, -156.25, -22.0,   6.0),
    make_engine(450.0,  287.5,  -10.0,  18.0),
    make_engine(450.0, -287.5,  -10.0,  18.0)
]

# 9. LANDING GEAR ASSEMBLY (22 WHEELS TOTAL: 2 NLG, 8 WLG, 12 BLG)
def make_wheel(x, y, z):
    return Part.makeCylinder(8.89, 6.6, App.Vector(x, y - 3.3, z), App.Vector(0, 1, 0))

def make_axle_with_wheels(x, y_center, z, y_spacing=12.0):
    w_left = make_wheel(x, y_center - y_spacing/2.0, z)
    w_right = make_wheel(x, y_center + y_spacing/2.0, z)
    axle_bar = Part.makeCylinder(2.5, y_spacing + 2.0, App.Vector(x, y_center - (y_spacing+2.0)/2.0, z), App.Vector(0, 1, 0))
    return Part.makeCompound([w_left, w_right, axle_bar])

nlg_strut = Part.makeCylinder(3.5, 50.0, App.Vector(140.0, 0.0, Z_GROUND), App.Vector(0, 0, 1))
nlg_wheels = make_axle_with_wheels(140.0, 0.0, Z_GROUND, 10.0)

def make_wlg_bogie(x_center, y_pos):
    strut = Part.makeCylinder(4.5, 50.0, App.Vector(x_center, y_pos, Z_GROUND), App.Vector(0, 0, 1))
    bogie_beam = Part.makeBox(28.0, 4.0, 5.0)
    bogie_beam.translate(App.Vector(x_center - 14.0, y_pos - 2.0, Z_GROUND - 2.5))
    axle1 = make_axle_with_wheels(x_center - 10.0, y_pos, Z_GROUND, 12.0)
    axle2 = make_axle_with_wheels(x_center + 10.0, y_pos, Z_GROUND, 12.0)
    return Part.makeCompound([strut, bogie_beam, axle1, axle2])

def make_blg_bogie(x_center, y_pos):
    strut = Part.makeCylinder(5.0, 45.0, App.Vector(x_center, y_pos, Z_GROUND), App.Vector(0, 0, 1))
    bogie_beam = Part.makeBox(42.0, 5.0, 6.0)
    bogie_beam.translate(App.Vector(x_center - 21.0, y_pos - 2.5, Z_GROUND - 3.0))
    axle1 = make_axle_with_wheels(x_center - 15.0, y_pos, Z_GROUND, 14.0)
    axle2 = make_axle_with_wheels(x_center,        y_pos, Z_GROUND, 14.0)
    axle3 = make_axle_with_wheels(x_center + 15.0, y_pos, Z_GROUND, 14.0)
    return Part.makeCompound([strut, bogie_beam, axle1, axle2, axle3])

landing_gears = [
    nlg_strut, nlg_wheels,
    make_wlg_bogie(420.0, 70.0), make_wlg_bogie(420.0, -70.0),
    make_blg_bogie(460.0, 38.0), make_blg_bogie(460.0, -38.0)
]

# 10. SEAMLESS AIRFRAME FUSION & ASSEMBLY COMPOUND
airframe_components = [fuselage, r_wing, l_wing, winglet_r, winglet_l, vtail, r_htail, l_htail, belly_fairing]
airframe_solid = airframe_components[0]
for comp in airframe_components[1:]:
    if comp.Volume < 0:
        comp.reverse()
    try:
        fused = airframe_solid.fuse(comp)
        if fused.isValid():
            airframe_solid = fused
        else:
            airframe_solid = Part.makeCompound([airframe_solid, comp])
    except Exception:
        airframe_solid = Part.makeCompound([airframe_solid, comp])

all_shapes = [airframe_solid] + canoes + engines + landing_gears
compound_shape = Part.makeCompound(all_shapes)

model_obj = doc.addObject("Part::Feature", "Airbus_A380_1to80_Complete")
model_obj.Shape = compound_shape
doc.recompute()

bbox = compound_shape.BoundBox
print("==================================================")
print("AIRBUS A380-800 1:80 MODEL GENERATION SUCCESSFUL!")
print(f"Total Bounding Box Length (X): {bbox.XLength:.2f} mm (Target: {OVERALL_LENGTH:.2f} mm)")
print(f"Total Bounding Box Span   (Y): {bbox.YLength:.2f} mm (Target: ~{WINGSPAN:.2f} mm)")
print(f"Total Bounding Box Height (Z): {bbox.ZLength:.2f} mm (Target: {TOTAL_AIRCRAFT_HEIGHT:.2f} mm)")
print("==================================================")

output_dir = r"c:\Users\Sudhish\OneDrive\Desktop\code\dev\FreeCAD-src\Output_Models"
os.makedirs(output_dir, exist_ok=True)

fcstd_path = os.path.join(output_dir, "Airbus_A380_1to80_Scale.FCStd")
step_path = os.path.join(output_dir, "Airbus_A380_1to80_Scale.step")
stl_path = os.path.join(output_dir, "Airbus_A380_1to80_Scale.stl")

doc.saveAs(fcstd_path)
compound_shape.exportStep(step_path)
compound_shape.exportStl(stl_path)

print(f"Saved native FreeCAD document: {fcstd_path}")
print(f"Exported STEP CAD solid file:     {step_path}")
print(f"Exported 3D printable STL mesh:  {stl_path}")
