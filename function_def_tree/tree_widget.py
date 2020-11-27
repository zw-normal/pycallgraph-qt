from typing import Optional

from PySide2.QtCore import Slot, QItemSelection
from PySide2.QtWidgets import QTreeView, QWidget

from function_def_tree.tree_model import FunctionDefTreeModel
from thread_controller import thread_constroller

class FunctionDefTreeWidget(QTreeView):

    def __init__(self, parent: Optional[QWidget] = ...):
        super().__init__(parent)
        self.setModel(FunctionDefTreeModel(self))
        self.setHeaderHidden(True)
        self.selectionModel().selectionChanged.connect(
            self.functionItemSelected)

    @Slot(QItemSelection, QItemSelection)
    def functionItemSelected(
            self, selected: QItemSelection, deselected: QItemSelection):
        func_def = selected[0].indexes()[0].internalPointer()
        if func_def.function is not None:
            thread_constroller.get_func_call_dot(func_def.function.id)
