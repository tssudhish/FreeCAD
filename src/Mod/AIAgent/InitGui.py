import FreeCAD
import FreeCADGui

class AIAgentWorkbench(FreeCADGui.Workbench):
    "AIAgent workbench object"
    MenuText = "AIAgent"
    ToolTip = "An AI Agent for FreeCAD"
    Icon = """
        /* XPM */
        static const char * aia_icon_xpm[] = {
        "16 16 2 1",
        "  c None",
        ". c #000000",
        "                ",
        "  ............  ",
        "  .          .  ",
        "  .  ......  .  ",
        "  .  .    .  .  ",
        "  .  .    .  .  ",
        "  .  ......  .  ",
        "  .          .  ",
        "  .  ......  .  ",
        "  .  .    .  .  ",
        "  .  .    .  .  ",
        "  .  ......  .  ",
        "  .          .  ",
        "  ............  ",
        "                "
        };
        """

    def Initialize(self):
        "This function is executed when FreeCAD starts"
        import AIAgentCommand
        self.appendToolbar("AIAgent", ["AIAgent_OpenPanel"])
        self.appendMenu("AIAgent", ["AIAgent_OpenPanel"])

    def Activated(self):
        "This function is executed when the workbench is activated"
        return

    def Deactivated(self):
        "This function is executed when the workbench is deactivated"
        return

    def ContextMenu(self, recipient):
        "This is executed whenever the user right-clicks on screen"
        pass

    def GetClassName(self):
        # this function is mandatory if this is a full python workbench
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(AIAgentWorkbench())
