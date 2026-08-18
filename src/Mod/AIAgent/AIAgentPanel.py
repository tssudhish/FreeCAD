import FreeCAD
import FreeCADGui
import os
import threading
import json
import socket

try:
    from PySide6 import QtWidgets, QtCore, QtGui, QtNetwork
    HAS_PYSIDE6 = True
except ImportError:
    try:
        from PySide2 import QtWidgets, QtCore, QtGui, QtNetwork
        HAS_PYSIDE6 = False
    except ImportError:
        pass # Handle PySide2/6 differences if needed

try:
    from google import genai
    from google.genai import types
    HAS_GOOGLE_GENAI = True
except ImportError:
    HAS_GOOGLE_GENAI = False

class FreeCADSocketServer(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.server = QtNetwork.QTcpServer(self)
        self.server.newConnection.connect(self.on_new_connection)
        
        # Listen on localhost port 5055
        if not self.server.listen(QtNetwork.QHostAddress.LocalHost, 5055):
            FreeCAD.Console.PrintError("AI Agent: Could not start TCP Server on port 5055. It might already be running.\n")
        else:
            FreeCAD.Console.PrintLog("AI Agent: TCP Socket Server listening on port 5055\n")
            
    def on_new_connection(self):
        socket = self.server.nextPendingConnection()
        socket.readyRead.connect(lambda: self.on_ready_read(socket))
        
    def on_ready_read(self, socket):
        data = socket.readAll()
        try:
            req = json.loads(str(data, encoding="utf-8"))
            action = req.get("action")
            params = req.get("params", {})
            
            if action == "run_code":
                code = params.get("code")
                result = self.execute_code(code)
                socket.write(json.dumps(result).encode("utf-8"))
            elif action == "get_context":
                context = self.get_context()
                socket.write(json.dumps({"status": "success", "result": context}).encode("utf-8"))
            else:
                socket.write(json.dumps({"status": "error", "error": f"Unknown action: {action}"}).encode("utf-8"))
        except Exception as e:
            try:
                socket.write(json.dumps({"status": "error", "error": str(e)}).encode("utf-8"))
            except:
                pass
        finally:
            socket.disconnectFromHost()

    def execute_code(self, code):
        try:
            # Re-verify document active state
            if not FreeCAD.ActiveDocument:
                FreeCAD.newDocument("Unnamed")
            
            # Execute python code in global scope
            exec(code, globals())
            FreeCAD.ActiveDocument.recompute()
            return {"status": "success", "result": "Code executed successfully and active document recomputed."}
        except Exception as e:
            return {"status": "error", "error": str(e)}
            
    def get_context(self):
        doc = FreeCAD.ActiveDocument
        if not doc:
            return {"active_document": None, "objects": []}
        
        objects = []
        for obj in doc.Objects:
            objects.append({
                "name": obj.Name,
                "label": obj.Label,
                "type": obj.TypeId
            })
        return {
            "active_document": doc.Name,
            "objects": objects
        }

_socket_server = None

class AIAgentPanel(QtWidgets.QDockWidget):
    code_generated = QtCore.Signal(str)
    error_occurred = QtCore.Signal(str)
    log_message = QtCore.Signal(str)

    def __init__(self):
        super().__init__("AI Agent")
        
        # Connect thread-safe signals
        self.code_generated.connect(self.execute_code)
        self.error_occurred.connect(self.handle_error)
        self.log_message.connect(self.handle_log)
        
        # Start socket server globally if not already running
        global _socket_server
        if _socket_server is None:
            _socket_server = FreeCADSocketServer()

        self.client = None
        self.chat_session = None

        self.initUI()
        
        # Trigger client initialization safely after construction
        QtCore.QTimer.singleShot(200, self.check_api_key_and_init)

    def handle_error(self, err_msg):
        FreeCAD.Console.PrintError(f"AI Agent: Error: {err_msg}\n")
        self.append_agent_message(f"LLM Error: {err_msg}")

    def handle_log(self, log_msg):
        FreeCAD.Console.PrintLog(f"AI Agent: {log_msg}\n")
        
    def initUI(self):
        self.setMinimumWidth(320)
        
        # Modern Premium Dark Styling sheet
        self.setStyleSheet("""
            QDockWidget {
                background-color: #1a1b26;
                color: #a9b1d6;
                font-family: 'Segoe UI', Helvetica, sans-serif;
            }
            QWidget#MainWidget {
                background-color: #1a1b26;
            }
            QTextEdit#ChatHistory {
                background-color: #16161e;
                color: #a9b1d6;
                border: 1px solid #383e5a;
                border-radius: 8px;
                padding: 8px;
                font-size: 11pt;
            }
            QLineEdit#InputField {
                background-color: #24283b;
                color: #c0caf5;
                border: 1px solid #383e5a;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 11pt;
            }
            QPushButton#SendBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7aa2f7, stop:1 #89ddff);
                color: #1a1b26;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton#SendBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #89ddff, stop:1 #bb9af7);
            }
            QComboBox#ModelSelector {
                background-color: #24283b;
                color: #c0caf5;
                border: 1px solid #383e5a;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 10pt;
                min-width: 140px;
            }
            QComboBox#ModelSelector QAbstractItemView {
                background-color: #16161e;
                color: #a9b1d6;
                selection-background-color: #3d59a1;
                selection-color: #ffffff;
                border: 1px solid #383e5a;
            }
            QLabel#ModelLabel {
                color: #565f89;
                font-size: 10pt;
                font-weight: bold;
            }
        """)

        widget = QtWidgets.QWidget()
        widget.setObjectName("MainWidget")
        layout = QtWidgets.QVBoxLayout()
        
        # Model selector header
        model_layout = QtWidgets.QHBoxLayout()
        model_label = QtWidgets.QLabel("Model:")
        model_label.setObjectName("ModelLabel")
        
        self.model_selector = QtWidgets.QComboBox()
        self.model_selector.setObjectName("ModelSelector")
        self.model_selector.addItems([
            "gemini-3.6-flash",
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "Ollama (local)"
        ])
        self.model_selector.currentIndexChanged.connect(self.on_model_changed)
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_selector)
        model_layout.addStretch()
        layout.addLayout(model_layout)
        
        # MCP Server Status Indicator
        status_layout = QtWidgets.QHBoxLayout()
        status_dot = QtWidgets.QLabel("●")
        status_dot.setStyleSheet("color: #9ece6a; font-size: 11pt; margin-left: 2px;") # Green dot
        status_text = QtWidgets.QLabel("MCP Server active on port 5055")
        status_text.setStyleSheet("color: #565f89; font-size: 9pt; font-weight: bold;")
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_text)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        self.chat_history = QtWidgets.QTextEdit()
        self.chat_history.setObjectName("ChatHistory")
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)
        
        input_layout = QtWidgets.QHBoxLayout()
        self.input_field = QtWidgets.QLineEdit()
        self.input_field.setObjectName("InputField")
        self.input_field.setPlaceholderText("Ask the agent to do something...")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QtWidgets.QPushButton("Send")
        self.send_btn.setObjectName("SendBtn")
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        widget.setLayout(layout)
        self.setWidget(widget)
        
        self.append_system_message("AI Agent initializing...")

    def check_api_key_and_init(self):
        if not HAS_GOOGLE_GENAI:
            self.append_system_message("Error: `google-genai` library not found. Please install it using `pixi` or check your environment.")
            return

        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            paths_to_check = [
                os.path.join(os.path.expanduser("~"), ".env"),
                os.path.join(os.path.expanduser("~"), ".freecad_ai_agent.env"),
                os.path.join(os.getcwd(), ".env")
            ]
            for p in paths_to_check:
                if os.path.exists(p):
                    try:
                        with open(p, "r") as f:
                            for line in f:
                                if line.startswith("GEMINI_API_KEY="):
                                    api_key = line.split("=", 1)[1].strip()
                                    if api_key.startswith(('"', "'")) and api_key.endswith(('"', "'")):
                                        api_key = api_key[1:-1]
                                    os.environ["GEMINI_API_KEY"] = api_key
                                    break
                    except Exception:
                        pass
                    if api_key:
                        break

        if not api_key:
            key_input, ok = QtWidgets.QInputDialog.getText(
                self, 
                "Gemini API Key Required", 
                "No GEMINI_API_KEY was found in environment or .env files.\n\nPlease enter your Gemini API Key:",
                QtWidgets.QLineEdit.Password
            )
            if ok and key_input.strip():
                api_key = key_input.strip()
                os.environ["GEMINI_API_KEY"] = api_key
                try:
                    save_path = os.path.join(os.path.expanduser("~"), ".freecad_ai_agent.env")
                    with open(save_path, "w") as f:
                        f.write(f"GEMINI_API_KEY={api_key}\n")
                    FreeCAD.Console.PrintLog(f"Saved Gemini API Key to {save_path}\n")
                except Exception as e:
                    FreeCAD.Console.PrintError(f"Could not save API Key: {e}\n")

        if api_key:
            try:
                selected_model = self.model_selector.currentText()
                self.client = genai.Client(api_key=api_key)
                self.chat_session = self.client.chats.create(
                    model=selected_model,
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            "You are a helpful AI assistant integrated into FreeCAD.\n"
                            "Your task is to generate Python code using the FreeCAD API to fulfill the user's request.\n"
                            "You can utilize any of FreeCAD's workbenches (e.g. Part, PartDesign, Sketcher, Draft, BIM).\n"
                            "Only return valid Python code that can be executed directly via `exec()`. Do not include markdown code blocks, just the raw code."
                        )
                    )
                )
                self.chat_history.clear()
                self.append_system_message(f"AI Agent Ready with {selected_model}. Describe what you want to construct!")
            except Exception as e:
                self.chat_history.clear()
                self.append_system_message(f"Error: Could not initialize Gemini Client: {str(e)}")
        else:
            self.chat_history.clear()
            self.append_system_message("Error: Gemini client failed to initialize. Gemini API Key is missing.")

    def on_model_changed(self):
        selected_model = self.model_selector.currentText()
        if selected_model == "Ollama (local)":
            self.append_system_message("Switched to local Ollama. Ensure Ollama is running ('ollama serve').")
            return

        if not self.client:
            return
        self.append_system_message(f"Switching to model: {selected_model}...")
        try:
            self.chat_session = self.client.chats.create(
                model=selected_model,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are a helpful AI assistant integrated into FreeCAD.\n"
                        "Your task is to generate Python code using the FreeCAD API to fulfill the user's request.\n"
                        "You can utilize any of FreeCAD's workbenches (e.g. Part, PartDesign, Sketcher, Draft, BIM).\n"
                        "Only return valid Python code that can be executed directly via `exec()`. Do not include markdown code blocks, just the raw code."
                    )
                )
            )
            self.append_system_message(f"AI Agent ready with {selected_model}!")
        except Exception as e:
            self.append_system_message(f"Error switching model: {str(e)}")

    def append_system_message(self, message):
        html = f"""
        <div style="margin: 8px 0px; text-align: center;">
            <span style="color: #565f89; font-size: 9pt; font-style: italic;">
                {message}
            </span>
        </div>
        """
        self.chat_history.insertHtml(html)
        self.scroll_to_bottom()

    def append_user_message(self, message):
        html = f"""
        <div style="margin: 8px 0px; text-align: right;">
            <div style="background-color: #3d59a1; color: #ffffff; border-radius: 8px; padding: 8px 12px; display: inline-block; max-width: 80%;">
                <b>You:</b><br>{message}
            </div>
        </div>
        """
        self.chat_history.insertHtml(html)
        self.scroll_to_bottom()

    def append_agent_message(self, message):
        # Format code blocks nicely
        import re
        message_formatted = message
        # Basic markdown to HTML code rendering
        message_formatted = re.sub(r"```python(.*?)```", r"<pre style='background-color:#1a1b26; border:1px solid #383e5a; padding:6px; border-radius:4px; font-family:Consolas, monospace; color:#9ece6a;'>\1</pre>", message_formatted, flags=re.DOTALL)
        message_formatted = message_formatted.replace("\n", "<br>")
        
        html = f"""
        <div style="margin: 8px 0px; text-align: left;">
            <div style="background-color: #24283b; color: #a9b1d6; border-radius: 8px; padding: 8px 12px; display: inline-block; max-width: 80%; border: 1px solid #383e5a;">
                <b>Agent:</b><br>{message_formatted}
            </div>
        </div>
        """
        self.chat_history.insertHtml(html)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        vbar = self.chat_history.verticalScrollBar()
        vbar.setValue(vbar.maximum())

    def get_freecad_context(self):
        doc = FreeCAD.ActiveDocument
        if not doc:
            return "No active document."
        
        context = f"Active Document: {doc.Name}\nObjects:\n"
        for obj in doc.Objects:
            context += f"- {obj.Name} ({obj.TypeId})\n"
        return context

    def execute_code(self, code):
        self.append_system_message(f"Executing generated script...")
        try:
            if not FreeCAD.ActiveDocument:
                FreeCAD.newDocument("Unnamed")
            exec(code, globals())
            FreeCAD.ActiveDocument.recompute()
            FreeCADGui.updateGui()
            self.append_system_message("Success: Changes rendered in 3D viewer.")
        except Exception as e:
            self.append_agent_message(f"Execution Error: {str(e)}")

    def send_message(self):
        selected_model = self.model_selector.currentText()
        if selected_model != "Ollama (local)":
            if not self.client or not hasattr(self, 'chat_session') or not self.chat_session:
                self.append_system_message("Error: LLM chat session not initialized.")
                return
            
        prompt = self.input_field.text()
        if not prompt:
            return
            
        self.input_field.clear()
        self.append_user_message(prompt)
        
        context = self.get_freecad_context()
        full_prompt = f"Current FreeCAD Context:\n{context}\n\nUser Request: {prompt}"
        
        # Run API call in a separate thread so UI doesn't freeze
        threading.Thread(target=self.call_llm, args=(full_prompt,)).start()

    def call_llm(self, prompt):
        self.log_message.emit("call_llm thread started.")
        selected_model = self.model_selector.currentText()
        if selected_model == "Ollama (local)":
            self.call_ollama(prompt)
            return

        try:
            self.log_message.emit("Sending prompt to Gemini...")
            response = self.chat_session.send_message(prompt)
            self.log_message.emit("Received response from Gemini.")
            code = response.text
            self.log_message.emit(f"Generated code:\n{code}")
            
            # Clean up markdown if the LLM still returns it
            if code.startswith("```python"):
                code = code[9:]
            if code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
                
            code = code.strip()
            
            self.code_generated.emit(code)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def call_ollama(self, prompt):
        import urllib.request
        import urllib.error
        import json
        
        self.log_message.emit("Sending prompt to local Ollama...")
        try:
            # 1. Discover models installed in Ollama
            model_name = "gemma2"  # fallback default
            try:
                with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as r:
                    data = json.loads(r.read().decode('utf-8'))
                    if data.get("models"):
                        model_name = data["models"][0]["name"]
                        self.log_message.emit(f"Auto-detected local Ollama model: {model_name}")
            except Exception:
                self.log_message.emit("Could not auto-detect Ollama models, using fallback 'gemma2'")
                
            # 2. Make generation request
            url = "http://localhost:11434/api/generate"
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": model_name,
                "prompt": prompt,
                "system": (
                    "You are a helpful AI assistant integrated into FreeCAD.\n"
                    "Your task is to generate Python code using the FreeCAD API to fulfill the user's request.\n"
                    "You can utilize any of FreeCAD's workbenches (e.g. Part, PartDesign, Sketcher, Draft, BIM).\n"
                    "Only return valid Python code that can be executed directly via `exec()`. Do not include markdown code blocks, just the raw code."
                ),
                "stream": False
            }
            
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=30) as r:
                res_data = json.loads(r.read().decode('utf-8'))
                code = res_data.get("response", "")
                self.log_message.emit(f"Received response from Ollama. Generated code:\n{code}")
                
                # Clean up markdown if the LLM still returns it
                if code.startswith("```python"):
                    code = code[9:]
                if code.startswith("```"):
                    code = code[3:]
                if code.endswith("```"):
                    code = code[:-3]
                    
                code = code.strip()
                self.code_generated.emit(code)
                
        except urllib.error.URLError as e:
            self.error_occurred.emit(f"Ollama connection failed: {e.reason}. Make sure Ollama is running ('ollama serve').")
        except Exception as e:
            self.error_occurred.emit(f"Ollama error: {str(e)}")
