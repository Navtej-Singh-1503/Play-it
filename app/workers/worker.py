from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerSignals(QObject):
    result = Signal(object); error = Signal(str); finished = Signal()


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__(); self.fn = fn; self.args = args; self.kwargs = kwargs; self.signals = WorkerSignals()
        self.setAutoDelete(True)
    @Slot()
    def run(self):
        try: self.signals.result.emit(self.fn(*self.args, **self.kwargs))
        except Exception as e: self.signals.error.emit(str(e))
        finally: self.signals.finished.emit()
