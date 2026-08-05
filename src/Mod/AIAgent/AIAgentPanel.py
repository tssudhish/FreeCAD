import FreeCAD
import FreeCADGui
from PySide import QtGui, QtCore
try:
    from PySide6 import QtWidgets, QtCore, QtGui
    HAS_PYSIDE6 = True
except ImportError:
    try:
        from PySide2 import QtWidgets, QtCore, QtGui
        HAS_PYSIDE6 = False
    except ImportError:
        pass # Handle PySide2/6 differences if needed

import os
import threading
try:
    from google import genai
    from google.genai import types
    HAS_GOOGLE_GENAI = True
except ImportError:
    HAS_GOOGLE_GENAI = False

class AIAgentPanel(QtWidgets.QDockWidget):
    def __init__(self):
        super().__init__("AI Agent")
        
        self.client = None
        if HAS_GOOGLE_GENAI:
            # Assumes GEMINI_API_KEY is in environment
            try:
                self.client = genai.Client()
            except Exception as e:
                FreeCAD.Console.PrintError(f"Could not initialize Gemini Client: {e}\n")

        self.initUI()
        
    def initUI(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        
        self.chat_history = QtWidgets.QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)
        
        input_layout = QtWidgets.QHBoxLayout()
        self.input_field = QtWidgets.QLineEdit()
        self.input_field.setPlaceholderText("Ask the agent to do something...")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QtWidgets.QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        widget.setLayout(layout)
        self.setWidget(widget)
        
        if not HAS_GOOGLE_GENAI:
            self.chat_history.append("<b>Error:</b> `google-genai` library not found. Please install it in FreeCAD's Python environment.")
        elif not self.client:
            self.chat_history.append("<b>Error:</b> Gemini client failed to initialize. Check GEMINI_API_KEY.")
        else:
            self.chat_history.append("<b>AI Agent ready.</b> Type a prompt to modify the FreeCAD document.")

    def get_freecad_context(self):
        doc = FreeCAD.ActiveDocument
        if not doc:
            return "No active document."
        
        context = f"Active Document: {doc.Name}\nObjects:\n"
        for obj in doc.Objects:
            context += f"- {obj.Name} ({obj.TypeId})\n"
        return context

    def execute_code(self, code):
        self.chat_history.append(f"<br><b>Agent executing code:</b><br><pre>{code}</pre>")
        try:
            exec(code, globals())
            FreeCAD.ActiveDocument.recompute()
            self.chat_history.append("<b>Success:</b> Code executed.")
        except Exception as e:
            self.chat_history.append(f"<b>Error during execution:</b> {str(e)}")

    def send_message(self):
        if not self.client:
            return
            
        prompt = self.input_field.text()
        if not prompt:
            return
            
        self.input_field.clear()
        self.chat_history.append(f"<br><b>You:</b> {prompt}")
        
        context = self.get_freecad_context()
        full_prompt = (
            "You are a helpful AI assistant integrated into FreeCAD.\n"
            "Your task is to generate Python code using the FreeCAD API to fulfill the user's request.\n"
            "Only return valid Python code that can be executed directly via `exec()`. Do not include markdown code blocks, just the raw code.\n\n"
            f"Current FreeCAD Context:\n{context}\n\n"
            f"User Request: {prompt}"
        )
        
        # Run API call in a separate thread so UI doesn't freeze
        threading.Thread(target=self.call_llm, args=(full_prompt,)).start()

    def call_llm(self, prompt):
        try:
            # We use gemini-2.5-flash as the default model
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            code = response.text
            # Clean up markdown if the LLM still returns it
            if code.startswith("```python"):
                code = code[9:]
            if code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
                
            code = code.strip()
            
            # Execute code back on main thread (safe for GUI/FreeCAD API)
            QtCore.QTimer.singleShot(0, lambda: self.execute_code(code))
        except Exception as e:
            QtCore.QTimer.singleShot(0, lambda: self.chat_history.append(f"<b>LLM Error:</b> {str(e)}"))
