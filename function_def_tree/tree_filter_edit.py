from PySide2.QtCore import Slot
from PySide2.QtWidgets import QLineEdit

from signal_hub import signalHub

class FunctionDefTreeFilterEdit(QLineEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText('Search a Function')
        self.textChanged.connect(self.filterFuncDefTree)

    @Slot(str)
    def filterFuncDefTree(self, text):
        signalHub.filterFuncDefTree.emit(text)
