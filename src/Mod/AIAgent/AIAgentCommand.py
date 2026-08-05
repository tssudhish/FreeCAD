import FreeCAD
import FreeCADGui
from AIAgentPanel import AIAgentPanel

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
        FreeCADGui.getMainWindow().addDockWidget(FreeCADGui.QtCore.Qt.RightDockWidgetArea, self.panel)
        self.panel.show()

FreeCADGui.addCommand('AIAgent_OpenPanel', OpenAIAgentPanelCommand())
