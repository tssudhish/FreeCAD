import os
import FreeCAD as App
import Part

print("Executing Complete Airbus A380 1:80 Scale Assembly...")

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
Z_GROUND = -60.20

# 1. OVOID (DOUBLE-BUBBLE) FUSELAGE PROFILE WIRE
def make_ovoid_wire(x, total_height, main_width, upper_width, z_center):
    h = max(total_height, 0.1)
    w_m = max(main_width / 2.0, 0.05)
    w_u = max(upper_width / 2.0, 0.05)
    pts_norm = [
        ( 0.0,    z_center + h*0.50),
        ( w_u*0.75, z_center + h*0.42),
        ( w_u,     z_center + DECK_SEPARATION*0.5),
        ( (w_m+w_u)*0.48, z_center),
        ( w_m,     z_center - DECK_SEPARATION*0.5),
        ( w_m*0.75, z_center - h*0.42),
        ( 0.0,    z_center - h*0.50),
        (-w_m*0.75, z_center - h*0.42),
        (-w_m,     z_center - DECK_SEPARATION*0.5),
        (-(w_m+w_u)*0.48, z_center),
        (-w_u,     z_center + DECK_SEPARATION*0.5),
        (-w_u*0.75, z_center + h*0.42),
        ( 0.0,    z_center + h*0.50)
    ]
    vecs = [App.Vector(x, py, pz) for py, pz in pts_norm]
    bspline = Part.BSplineCurve()
    bspline.makeC1Continuous()
    bspline.interpolate(vecs)
    return Part.Wire([bspline.toShape()])

# 2. AIRFOIL WIRES
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
    bspline.makeC1Continuous()
    bspline.interpolate(vecs)
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
    bspline.makeC1Continuous()
    bspline.interpolate(vecs)
    return Part.Wire([bspline.toShape()])

# FUSELAGE & BELLY FAIRING
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
belly_wires = [Part.Wire([Part.Ellipse(App.Vector(x_b, 0, z_b), App.Vector(0, w_b/2.0, 0), App.Vector(0, 0, h_b/2.0)).toShape()]) for x_b, w_b, h_b, z_b in belly_specs]
belly_fairing = Part.makeLoft(belly_wires, True)

# GULL WINGS
wing_stations_right = [
    (  2.0,   300.0, -16.0, 230.0, 0.13),
    ( 44.625, 328.0, -14.0, 210.0, 0.12),
    (100.0,   372.0,  -4.0, 182.0, 0.11),
    (156.25,  412.0,   6.0, 160.0, 0.11),
    (287.5,   490.0,  18.0, 114.0, 0.10),
    (480.0,   605.0,  36.0,  43.0, 0.09),
    (498.4,   616.0,  38.5,  35.0, 0.08)
]
r_wing = Part.makeLoft([make_airfoil_xy(x, y, z, c, t) for y, x, z, c, t in wing_stations_right], True)
l_wing = Part.makeLoft([make_airfoil_xy(x, -y, z, c, t) for y, x, z, c, t in reversed(wing_stations_right)], True)

def make_winglet(y_sign):
    y_pos = 498.4 * y_sign
    pts = [
        App.Vector(616.0, y_pos, 30.0),
        App.Vector(651.0, y_pos, 30.0),
        App.Vector(645.0, y_pos + 2.0*y_sign, 68.0),
        App.Vector(628.0, y_pos + 2.0*y_sign, 68.0),
        App.Vector(616.0, y_pos, 30.0)
    ]
    poly = Part.makePolygon(pts)
    face = Part.Face(poly)
    return face.extrude(App.Vector(0, 1.5*y_sign, 0))

winglet_r = make_winglet(1)
winglet_l = make_winglet(-1)

# FLAP TRACK CANOES
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

# STABILIZERS
vtail_stations = [
    ( 30.0,   650.0, 0.0, 180.0, 0.10),
    (100.0,   705.0, 0.0, 125.0, 0.09),
    (170.0,   755.0, 0.0,  80.0, 0.08),
    (240.925, 788.0, 0.0,  52.0, 0.07)
]
vtail = Part.makeLoft([make_airfoil_xz(x, y, z, c, t) for z, x, y, c, t in vtail_stations], True)

htail_stations_right = [
    (  2.0, 740.0, 15.0, 110.0, 0.09),
    ( 60.0, 768.0, 18.0,  86.0, 0.08),
    (130.0, 800.0, 22.0,  58.0, 0.08),
    (190.0, 828.0, 25.5,  35.0, 0.07)
]
r_htail = Part.makeLoft([make_airfoil_xy(x, y, z, c, t) for y, x, z, c, t in htail_stations_right], True)
l_htail = Part.makeLoft([make_airfoil_xy(x, -y, z, c, t) for y, x, z, c, t in reversed(htail_stations_right)], True)

# ENGINES & PYLONS
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
    exhaust_cone = Part.makeCone(12.0, 1.0, 20.0, App.Vector(x_end - 8.0, y_pos, z_center), App.Vector(1, 0, 0))
    pylon_height = wing_z - z_center + 6.0
    pylon_box = Part.makeBox(48.0, 3.5, pylon_height)
    pylon_box.translate(App.Vector(x_start + 10.0, y_pos - 1.75, z_center + r_max - 4.0))
    return Part.makeCompound([nacelle, exhaust_cone, pylon_box])

engines = [
    make_engine(370.0,  156.25, -22.0,   6.0),
    make_engine(370.0, -156.25, -22.0,   6.0),
    make_engine(450.0,  287.5,  -10.0,  18.0),
    make_engine(450.0, -287.5,  -10.0,  18.0)
]

# LANDING GEAR ASSEMBLY (22 WHEELS TOTAL)
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

# CREATE COMPOUND FOR CLEAN NON-DESTRUCTIVE CAD ASSEMBLY & EXPORT
all_shapes = [fuselage, belly_fairing, r_wing, l_wing, winglet_r, winglet_l, vtail, r_htail, l_htail] + canoes + engines + landing_gears
compound_shape = Part.makeCompound(all_shapes)

model_obj = doc.addObject("Part::Feature", "Airbus_A380_1to80_Complete")
model_obj.Shape = compound_shape
doc.recompute()

bbox = compound_shape.BoundBox
print("==================================================")
print("AIRBUS A380-800 1:80 MODEL GENERATION SUCCESSFUL!")
print(f"Total Bounding Box Length (X): {bbox.XLength:.2f} mm (Target: {OVERALL_LENGTH:.2f} mm / {OVERALL_LENGTH/10.0:.2f} cm)")
print(f"Total Bounding Box Span   (Y): {bbox.YLength:.2f} mm (Target: ~996.88 mm / {996.88/10.0:.2f} cm)")
print(f"Total Bounding Box Height (Z): {bbox.ZLength:.2f} mm (Target: {TOTAL_AIRCRAFT_HEIGHT:.2f} mm / {TOTAL_AIRCRAFT_HEIGHT/10.0:.2f} cm)")
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
