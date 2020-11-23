from PySide2.QtCore import QObject, Signal, Slot


class SignalHub(QObject):

    funcDefTreeFuncSel = Signal(str)

    @Slot(int)
    @staticmethod
    def getFuncCallers(funcId):
        pass

signalHub = SignalHub()
