from PyQt5.QtCore import QThread, pyqtSignal
from ..ai_service import generate_ai_response

class AIWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, query, context):
        super().__init__()
        self.query = query
        self.context = context

    def run(self):
        try:
            result = generate_ai_response(self.query, self.context)
            if result:
                self.finished.emit(result)
            else:
                self.error.emit("No response from AI service.")
        except Exception as e:
            self.error.emit(str(e))
