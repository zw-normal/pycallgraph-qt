from PySide2.QtCore import QObject, Signal, Slot

from function_call_graph import GraphThread


class SignalHub(QObject):

    funcCallDotGet = Signal(str)

    def __init__(self):
        super().__init__()
        self.graphThread = None

    def getFuncCallDot(self, func_id: int):
        if self.graphThread:
            self.graphThread.resultReady.disconnect()
            self.graphThread.stop()
        self.graphThread = GraphThread(func_id)
        self.graphThread.resultReady.connect(self.getFuncCallDone)
        self.graphThread.start()

    @Slot(str)
    def getFuncCallDone(self, func_call_dot):
        self.funcCallDotGet.emit(func_call_dot)

    def stopFuncCallGraphThread(self):
        if self.graphThread:
            self.graphThread.resultReady.disconnect()
            self.graphThread.stop()
            self.graphThread = None


signalHub = SignalHub()
