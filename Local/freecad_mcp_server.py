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
def execute_python_cad_script(python_code: str) -> str:
    """Execute arbitrary FreeCAD Python scripting code safely."""
    try:
        # Provide App and Part in local scope
        local_scope = {"App": App, "Part": Part}
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

if __name__ == "__main__":
    mcp.run(transport="stdio")
