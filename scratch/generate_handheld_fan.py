import math
import os
import FreeCAD as App
import Part
from FreeCAD import Base

def create_fan_assembly():
    doc_name = "HandheldFan_Assembly"
    if doc_name in App.listDocuments():
        App.closeDocument(doc_name)
    doc = App.newDocument(doc_name)
    
    print("Building 3D Handheld Fan Assembly...")

    # -------------------------------------------------------------
    # 1. Rechargeable 18650 Battery Cell (Ø18mm x 65mm)
    # -------------------------------------------------------------
    battery_body = Part.makeCylinder(9.0, 65.0, Base.Vector(0, 0, 10), Base.Vector(0, 0, 1))
    pos_nib = Part.makeCylinder(2.75, 2.0, Base.Vector(0, 0, 75), Base.Vector(0, 0, 1))
    neg_cap = Part.makeCylinder(8.5, 1.0, Base.Vector(0, 0, 9), Base.Vector(0, 0, 1))
    battery_shape = battery_body.fuse(pos_nib).fuse(neg_cap)
    
    obj_battery = doc.addObject("Part::Feature", "Battery_18650")
    obj_battery.Shape = battery_shape
    obj_battery.Label = "18650 Li-ion Battery"

    # -------------------------------------------------------------
    # 2. USB-C Port & Charging PCB Assembly (Bottom Base)
    # -------------------------------------------------------------
    pcb_plate = Part.makeBox(18.0, 18.0, 1.6, Base.Vector(-9.0, -9.0, 4.0))
    usbc_housing = Part.makeBox(9.0, 7.5, 3.4, Base.Vector(-4.5, -3.75, 0.6))
    usbc_slot = Part.makeBox(6.8, 6.5, 1.4, Base.Vector(-3.4, -3.25, 0.6))
    usbc_port = usbc_housing.cut(usbc_slot)
    pcb_shape = pcb_plate.fuse(usbc_port)
    
    obj_pcb = doc.addObject("Part::Feature", "USBC_Port_PCB")
    obj_pcb.Shape = pcb_shape
    obj_pcb.Label = "USB-C Port & PCB"

    # -------------------------------------------------------------
    # 3. Handle Housing (Ergonomic grip, battery core, USB-C cutout)
    # -------------------------------------------------------------
    outer_handle = Part.makeCylinder(16.0, 105.0, Base.Vector(0, 0, 5), Base.Vector(0, 0, 1))
    base_flange = Part.makeCylinder(17.5, 5.0, Base.Vector(0, 0, 0), Base.Vector(0, 0, 1))
    neck_cone = Part.makeCone(16.0, 12.5, 20.0, Base.Vector(0, 0, 110), Base.Vector(0, 0, 1))
    head_mount_block = Part.makeBox(22.0, 24.0, 20.0, Base.Vector(-11.0, 10.0, 122.0))
    
    handle_solid = outer_handle.fuse(base_flange).fuse(neck_cone).fuse(head_mount_block)
    
    # Internal cutouts
    battery_cavity = Part.makeCylinder(10.0, 92.0, Base.Vector(0, 0, 5.6), Base.Vector(0, 0, 1))
    usbc_cutout = Part.makeBox(9.6, 4.2, 6.0, Base.Vector(-4.8, -2.1, 0))
    button_cutout = Part.makeCylinder(4.2, 10.0, Base.Vector(0, 12.0, 85.0), Base.Vector(0, 1, 0))
    wire_pass = Part.makeCylinder(5.0, 35.0, Base.Vector(0, 0, 97.0), Base.Vector(0, 0, 1))
    
    handle_shape = handle_solid.cut(battery_cavity).cut(usbc_cutout).cut(button_cutout).cut(wire_pass)
    
    obj_handle = doc.addObject("Part::Feature", "Handle_Housing")
    obj_handle.Shape = handle_shape
    obj_handle.Label = "Handle Housing Shell"

    # -------------------------------------------------------------
    # 4. Power Switch Button (Front Handle)
    # -------------------------------------------------------------
    button_cap = Part.makeCylinder(4.0, 5.0, Base.Vector(0, 13.0, 85.0), Base.Vector(0, 1, 0))
    button_bezel = Part.makeCylinder(5.0, 1.2, Base.Vector(0, 15.2, 85.0), Base.Vector(0, 1, 0))
    button_shape = button_cap.fuse(button_bezel)
    
    obj_button = doc.addObject("Part::Feature", "Power_Button")
    obj_button.Shape = button_shape
    obj_button.Label = "Power Switch Button"

    # -------------------------------------------------------------
    # 5. DC Motor Assembly & Drive Shaft
    # -------------------------------------------------------------
    motor_body = Part.makeCylinder(12.0, 14.0, Base.Vector(0, 23.0, 142.0), Base.Vector(0, 1, 0))
    motor_rear = Part.makeCylinder(4.0, 3.0, Base.Vector(0, 20.0, 142.0), Base.Vector(0, 1, 0))
    motor_front = Part.makeCylinder(4.0, 2.5, Base.Vector(0, 37.0, 142.0), Base.Vector(0, 1, 0))
    motor_shaft = Part.makeCylinder(1.0, 10.0, Base.Vector(0, 39.5, 142.0), Base.Vector(0, 1, 0))
    
    motor_shape = motor_body.fuse(motor_rear).fuse(motor_front).fuse(motor_shaft)
    
    obj_motor = doc.addObject("Part::Feature", "Motor_Assembly")
    obj_motor.Shape = motor_shape
    obj_motor.Label = "DC Motor & Drive Shaft"

    # -------------------------------------------------------------
    # 6. Rear Grille & Motor Enclosure
    # -------------------------------------------------------------
    rear_outer_rim = Part.makeCylinder(43.0, 26.0, Base.Vector(0, 22.0, 142.0), Base.Vector(0, 1, 0)).cut(
        Part.makeCylinder(41.2, 26.0, Base.Vector(0, 22.0, 142.0), Base.Vector(0, 1, 0))
    )
    motor_cup = Part.makeCylinder(13.5, 15.0, Base.Vector(0, 22.5, 142.0), Base.Vector(0, 1, 0)).cut(
        Part.makeCylinder(12.2, 15.0, Base.Vector(0, 22.5, 142.0), Base.Vector(0, 1, 0))
    )
    rear_wall = Part.makeCylinder(43.0, 2.0, Base.Vector(0, 22.0, 142.0), Base.Vector(0, 1, 0))
    
    # Air intake slots cut into rear wall
    air_slots = None
    for i in range(8):
        angle = math.radians(i * 45.0 + 22.5)
        rx = 26.0 * math.cos(angle)
        rz = 26.0 * math.sin(angle)
        slot = Part.makeCylinder(6.5, 4.0, Base.Vector(rx, 21.0, 142.0 + rz), Base.Vector(0, 1, 0))
        rear_wall = rear_wall.cut(slot)
        
    rear_wall = rear_wall.cut(Part.makeCylinder(12.2, 4.0, Base.Vector(0, 21.0, 142.0), Base.Vector(0, 1, 0)))
    
    # 6 Radial Spokes
    spokes = []
    for i in range(6):
        angle = math.radians(i * 60.0)
        spoke = Part.makeBox(2.4, 2.0, 28.0, Base.Vector(-1.2, 23.0, 128.0))
        spoke.rotate(Base.Vector(0, 24.0, 142.0), Base.Vector(0, 1, 0), i * 60.0)
        spokes.append(spoke)
        
    rear_housing = rear_outer_rim.fuse(motor_cup).fuse(rear_wall)
    for sp in spokes:
        rear_housing = rear_housing.fuse(sp)
        
    obj_rear_grille = doc.addObject("Part::Feature", "Rear_Grille_Housing")
    obj_rear_grille.Shape = rear_housing
    obj_rear_grille.Label = "Rear Grille & Motor Shell"

    # -------------------------------------------------------------
    # 7. Fan Rotor (5 Aerodynamic Twisted Blades + Central Hub)
    # -------------------------------------------------------------
    hub_core = Part.makeCylinder(9.0, 8.0, Base.Vector(0, 39.0, 142.0), Base.Vector(0, 1, 0))
    hub_bore = Part.makeCylinder(1.05, 8.0, Base.Vector(0, 39.0, 142.0), Base.Vector(0, 1, 0))
    hub_nose = Part.makeCone(9.0, 4.0, 3.5, Base.Vector(0, 47.0, 142.0), Base.Vector(0, 1, 0))
    rotor_hub = hub_core.cut(hub_bore).fuse(hub_nose)
    
    # Build 5 aerodynamic blades
    blades = []
    for i in range(5):
        angle_deg = i * 72.0
        # Blade geometry: angled plate extending outwards
        blade_box = Part.makeBox(2.2, 8.0, 29.0, Base.Vector(-1.1, 39.5, 149.0))
        # Twist / Pitch angle (~24 deg)
        blade_box.rotate(Base.Vector(0, 43.5, 149.0), Base.Vector(0, 1, 0), 24.0)
        # Radial position rotation
        blade_box.rotate(Base.Vector(0, 43.5, 142.0), Base.Vector(0, 1, 0), angle_deg)
        blades.append(blade_box)
        
    fan_rotor_shape = rotor_hub
    for b in blades:
        fan_rotor_shape = fan_rotor_shape.fuse(b)
        
    obj_fan_rotor = doc.addObject("Part::Feature", "Fan_Rotor_5Blade")
    obj_fan_rotor.Shape = fan_rotor_shape
    obj_fan_rotor.Label = "5-Blade Fan Rotor"

    # -------------------------------------------------------------
    # 8. Front Safety Grille Cover
    # -------------------------------------------------------------
    front_outer_rim = Part.makeCylinder(43.0, 8.0, Base.Vector(0, 48.0, 142.0), Base.Vector(0, 1, 0)).cut(
        Part.makeCylinder(41.2, 8.0, Base.Vector(0, 48.0, 142.0), Base.Vector(0, 1, 0))
    )
    front_center_badge = Part.makeCylinder(11.0, 2.5, Base.Vector(0, 53.5, 142.0), Base.Vector(0, 1, 0))
    
    # Concentric Wire Rings
    ring1 = Part.makeTorus(19.0, 1.0, Base.Vector(0, 54.5, 142.0), Base.Vector(0, 1, 0))
    ring2 = Part.makeTorus(29.0, 1.0, Base.Vector(0, 54.5, 142.0), Base.Vector(0, 1, 0))
    ring3 = Part.makeTorus(37.5, 1.0, Base.Vector(0, 54.5, 142.0), Base.Vector(0, 1, 0))
    
    front_grille_shape = front_outer_rim.fuse(front_center_badge).fuse(ring1).fuse(ring2).fuse(ring3)
    
    # 8 Radial Guard Ribs
    for i in range(8):
        angle_deg = i * 45.0
        rib = Part.makeBox(1.8, 1.8, 31.0, Base.Vector(-0.9, 53.6, 126.5))
        rib.rotate(Base.Vector(0, 54.5, 142.0), Base.Vector(0, 1, 0), angle_deg)
        front_grille_shape = front_grille_shape.fuse(rib)
        
    obj_front_grille = doc.addObject("Part::Feature", "Front_Safety_Grille")
    obj_front_grille.Shape = front_grille_shape
    obj_front_grille.Label = "Front Safety Grille"

    doc.recompute()
    print("Recomputed FreeCAD Document successfully!")
    return doc_name

if __name__ == "__main__":
    create_fan_assembly()
