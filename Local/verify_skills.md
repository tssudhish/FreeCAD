# Verification Prompts for FreeCAD Workbench Skills

Use these prompts in a new chat to verify that the agent successfully reads and implements the guidelines from the newly added workspace skills (`.agents/skills/`).

---

## 1. Sketcher Verification
*   **Prompt to type in chat:**
    > Use the Sketcher workbench to programmatically create a sketch named "BaseSketch" inside a new document "TestDoc". Add a line segment from (0,0) to (10,0) and constrain it to be horizontal.
*   **How to confirm it worked:**
    - The agent should call `execute_python_cad_script`.
    - The code inside should import `Sketcher` and use the pattern:
      `sketch.addGeometry(Part.LineSegment(...))` and `sketch.addConstraint(Sketcher.Constraint('Horizontal', line_id))`.

---

## 2. PartDesign Verification
*   **Prompt to type in chat:**
    > Write and execute a Python script to create a PartDesign Body named "BracketBody" and add a Pad feature of length 15.0 mm linked to a profile sketch named "MainProfile".
*   **How to confirm it worked:**
    - The script should add the sketch to the body (`body.addObject(sketch)`) before creating the Pad.
    - It should construct a `PartDesign::Pad` and set `pad.Profile = sketch` and `pad.Length = 15.0` as defined in the skill guidelines.

---

## 3. Part (CSG) Verification
*   **Prompt to type in chat:**
    > Write a FreeCAD Part script that builds a 50x50x50 Box and a Cylinder with a radius of 10 and height of 60. Then, perform a boolean Cut subtraction to remove the Cylinder from the center of the Box.
*   **How to confirm it worked:**
    - The agent should use `Part::Box` and `Part::Cylinder`.
    - It should instantiate a `Part::Cut` and assign `.Base` (the box) and `.Tool` (the cylinder).

---

## 4. Path (CAM) Verification
*   **Prompt to type in chat:**
    > Create a custom toolpath in FreeCAD that plunges to Z-2.0, cuts linearly to coordinate X30 Y10, and then retracts to a safe height of Z5.0. Output the generated G-code.
*   **How to confirm it worked:**
    - The script should compile a list of `Path.Command` instructions (e.g. `G1 Z-2.0`, `G1 X30 Y10`, `G0 Z5.0`).
    - The agent should construct `Path.Path(commands)` and call `toGCode()`.

---

## 5. Mesh Verification
*   **Prompt to type in chat:**
    > Write a Python script to tessellate a Part shape object named "BasePart" into a mesh with a linear deflection precision of 0.05 mm, and add it to the active document.
*   **How to confirm it worked:**
    - The agent should import `MeshPart` and use `MeshPart.meshFromShape(Shape=..., LinearDeflection=0.05)`.
    - It should assign the result to a `Mesh::Feature`'s `.Mesh` property.

---

## 6. Assembly Verification
*   **Prompt to type in chat:**
    > Programmatically set up a new Assembly container named "CarAssembly" and add a fixed joint constraint connecting "WheelPart" to "AxlePart".
*   **How to confirm it worked:**
    - The script should instantiate an `Assembly::Assembly` container.
    - It should create an `Assembly::JointFixed` and configure `.Elements` with a tuple mapping the parts and target faces.
