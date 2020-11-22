from typing import Dict

from PySide2.QtCore import QObject, Signal


class SignalHub(QObject):
    func_call_tree = Signal(Dict)


signalHub = SignalHub()
