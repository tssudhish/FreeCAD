import sys
import json
import socket
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FreeCAD")

def send_to_freecad(action: str, params: dict = None) -> dict:
    if params is None:
        params = {}
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10.0)
        s.connect(("127.0.0.1", 5055))
        payload = json.dumps({"action": action, "params": params})
        s.sendall(payload.encode("utf-8"))
        
        # Read response until connection is closed or complete JSON is read
        data = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
            # Try to decode to check if it's a valid JSON (in case sender closes connection)
            try:
                decoded = data.decode("utf-8")
                json.loads(decoded)
                break
            except ValueError:
                continue
                
        if not data:
            return {"status": "error", "error": "No response from FreeCAD"}
        return json.loads(data.decode("utf-8"))
    except ConnectionRefusedError:
        return {"status": "error", "error": "Could not connect to FreeCAD on port 5055. Ensure FreeCAD is running and the AI Agent panel is open."}
    except Exception as e:
        return {"status": "error", "error": f"Communication error: {str(e)}"}

@mcp.tool()
def run_python_code(code: str) -> str:
    """Execute Python code within the active FreeCAD instance.
    The code runs in the main GUI thread, allowing you to manipulate documents, create shapes, and modify objects.
    Always call FreeCAD.ActiveDocument.recompute() at the end if you make changes.
    """
    res = send_to_freecad("run_code", {"code": code})
    if res.get("status") == "success":
        return f"Success:\n{res.get('result')}"
    else:
        return f"Error:\n{res.get('error')}"

@mcp.tool()
def get_active_document_context() -> str:
    """Retrieve details about the active FreeCAD document, including its name and list of objects."""
    res = send_to_freecad("get_context")
    if res.get("status") == "success":
        return json.dumps(res.get("result"), indent=2)
    else:
        return f"Error:\n{res.get('error')}"

if __name__ == "__main__":
    mcp.run()
