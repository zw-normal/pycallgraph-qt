from typing import Dict

from PySide2.QtCore import QObject, Signal


class SignalHub(QObject):
    functionCallTree = Signal(str)


signalHub = SignalHub()
