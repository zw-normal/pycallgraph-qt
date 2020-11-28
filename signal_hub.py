from PySide2.QtCore import QObject, Signal, Slot


class SignalHub(QObject):

    # Handled by MainWindow
    showFuncDefMessageBox = Signal(str)
    showStatusBarMessage = Signal(str)

    # Handled by FunctionDefTreeModel
    filterFuncDefTree = Signal(str)

    # Handled by resource/index.js
    funcCallDotProgress = Signal(str)
    funcCallDotGet = Signal(str)

    # Handled by multiple widgets
    dataFileOpened = Signal()
    exitingApp = Signal()

    def __init__(self):
        super().__init__()

    @Slot(str)
    def getFuncCallDone(self, func_call_dot: str):
        self.funcCallDotGet.emit(func_call_dot)

    @Slot(str)
    def funcCallDotNodeSel(self, func_id: str):
        self.showFuncDefMessageBox.emit(func_id)


signalHub = SignalHub()
