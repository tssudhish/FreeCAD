import sys
import os
try:
    from mcp.server import MCPServer as FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

# 1. Path to built FreeCAD libraries
CANDIDATE_PATHS = [
    r"C:\Users\Sudhish\OneDrive\Desktop\code\dev\FreeCAD-src\.pixi\envs\default\Library\bin",
    r"C:\Users\Sudhish\OneDrive\Desktop\code\dev\FreeCAD-src\build\bin",
    r"C:\Users\Sudhish\OneDrive\Desktop\code\dev\FreeCAD-src\build\debug\bin",
    r"C:\Program Files\FreeCAD\bin",
]
for p in CANDIDATE_PATHS:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

# 2. Import FreeCAD C++ Python extension modules
try:
    import FreeCAD as App
    import Part
except ImportError as e:
    print(f"Error importing FreeCAD: {e}", file=sys.stderr)
    sys.exit(1)

# Import other workbenches safely
WORKBENCHES = {
    "FreeCAD": App,
    "Part": Part,
}
for name in ["PartDesign", "Sketcher", "ObjectsFem", "Fem", "Mesh", "Draft"]:
    try:
        mod = __import__(name)
        WORKBENCHES[name] = mod
    except ImportError:
        pass

# 3. Initialize FastMCP Server
mcp = FastMCP("FreeCAD Automation Server")

@mcp.tool()
def create_new_document(doc_name: str = "Unnamed") -> str:
    """Create a new CAD document in FreeCAD."""
    doc = App.newDocument(doc_name)
    return f"Created document: {doc.Name}"

@mcp.tool()
def create_box(doc_name: str, object_name: str, length: float, width: float, height: float) -> str:
    """Create a 3D parametric Box inside a specified document."""
    doc = App.getDocument(doc_name) if doc_name in App.listDocuments() else App.newDocument(doc_name)
    box_obj = doc.addObject("Part::Box", object_name)
    box_obj.Length = length
    box_obj.Width = width
    box_obj.Height = height
    doc.recompute()
    return f"Created Box '{object_name}' ({length}x{width}x{height} mm) in document '{doc.Name}'"

@mcp.tool()
def export_shape(doc_name: str, object_name: str, export_path: str, format_type: str = "STEP") -> str:
    """Export a CAD object to STEP, IGES, or STL file format."""
    doc = App.getDocument(doc_name)
    obj = doc.getObject(object_name)
    if not obj or not hasattr(obj, "Shape"):
        return f"Error: Object '{object_name}' with valid shape not found."
    
    os.makedirs(os.path.dirname(os.path.abspath(export_path)), exist_ok=True)
    
    format_lower = format_type.lower()
    if format_lower in ["step", "stp"]:
        obj.Shape.exportStep(export_path)
    elif format_lower in ["stl"]:
        obj.Shape.exportStl(export_path)
    elif format_lower in ["iges", "igs"]:
        obj.Shape.exportIges(export_path)
    else:
        return f"Unsupported format: {format_type}"
        
    return f"Successfully exported '{object_name}' to '{export_path}' ({format_type})"

@mcp.tool()
def list_available_workbenches() -> list:
    """List all the FreeCAD Python workbenches and modules successfully loaded in this environment."""
    return list(WORKBENCHES.keys())

@mcp.tool()
def execute_python_cad_script(python_code: str) -> str:
    """Execute arbitrary FreeCAD Python scripting code safely."""
    try:
        # Provide loaded workbenches in local scope (including App, Part, PartDesign, Sketcher, Fem, ObjectsFem, etc.)
        local_scope = WORKBENCHES.copy()
        exec(python_code, local_scope)
        return "Script executed successfully."
    except Exception as e:
        return f"Script execution error: {str(e)}"

@mcp.tool()
def inspect_document(doc_name: str) -> dict:
    """Inspect all objects, dimensions, properties, and hierarchy of a document."""
    doc = App.getDocument(doc_name)
    if not doc:
        return {"error": f"Document '{doc_name}' not found."}
    
    objects_summary = []
    for obj in doc.Objects:
        info = {
            "Name": obj.Name,
            "Label": obj.Label,
            "TypeId": obj.TypeId,
        }
        if hasattr(obj, "Shape") and obj.Shape:
            info["Volume"] = obj.Shape.Volume
            info["Area"] = obj.Shape.Area
            info["BoundingBox"] = str(obj.Shape.BoundBox)
        objects_summary.append(info)

    return {
        "DocumentName": doc.Name,
        "ObjectCount": len(doc.Objects),
        "Objects": objects_summary
    }

@mcp.tool()
def create_fem_analysis(doc_name: str, analysis_name: str = "Analysis") -> str:
    """Create a Finite Element Analysis (FEM) container, add a CalculiX CCX solver, and a solid material."""
    if "ObjectsFem" not in WORKBENCHES:
        return "Error: FEM workbench (ObjectsFem module) is not available in the current FreeCAD installation."
    
    doc = App.getDocument(doc_name) if doc_name in App.listDocuments() else App.newDocument(doc_name)
    ObjectsFem = WORKBENCHES["ObjectsFem"]
    
    analysis_obj = ObjectsFem.makeAnalysis(doc, analysis_name)
    solver_obj = ObjectsFem.makeSolverCalculiXCcxTools(doc, "CalculiXSolver")
    solver_obj.GeometricalNonlinearity = 'linear'
    solver_obj.ThermoMechSteadyState = True
    analysis_obj.addObject(solver_obj)
    
    material_obj = ObjectsFem.makeMaterialSolid(doc, "SolidMaterial")
    mat = material_obj.Material
    mat['Name'] = "Steel-Generic"
    mat['YoungsModulus'] = "210000 MPa"
    mat['PoissonRatio'] = "0.30"
    mat['Density'] = "7900 kg/m^3"
    material_obj.Material = mat
    analysis_obj.addObject(material_obj)
    
    doc.recompute()
    return f"Successfully created FEM Analysis '{analysis_name}' with CalculiX solver and Steel-Generic material in document '{doc.Name}'."

@mcp.tool()
def create_part_design_body(doc_name: str, body_name: str = "Body") -> str:
    """Create a PartDesign::Body container inside a specified document."""
    doc = App.getDocument(doc_name) if doc_name in App.listDocuments() else App.newDocument(doc_name)
    body_obj = doc.addObject("PartDesign::Body", body_name)
    doc.recompute()
    return f"Created PartDesign Body '{body_name}' in document '{doc.Name}'"

if __name__ == "__main__":
    mcp.run(transport="stdio")
