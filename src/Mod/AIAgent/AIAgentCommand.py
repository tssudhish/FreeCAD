import FreeCAD
import FreeCADGui
from AIAgentPanel import AIAgentPanel

try:
    from PySide6 import QtCore
except ImportError:
    try:
        from PySide2 import QtCore
    except ImportError:
        from PySide import QtCore

class OpenAIAgentPanelCommand:
    def __init__(self):
        self.panel = None

    def GetResources(self):
        return {'Pixmap'  : 'Std_Tool1',
                'MenuText': 'Open AI Agent',
                'ToolTip' : 'Open the AI Agent Chat Panel'}

    def Activated(self):
        if not self.panel:
            self.panel = AIAgentPanel()
        FreeCADGui.getMainWindow().addDockWidget(QtCore.Qt.RightDockWidgetArea, self.panel)
        self.panel.show()

FreeCADGui.addCommand('AIAgent_OpenPanel', OpenAIAgentPanelCommand())
