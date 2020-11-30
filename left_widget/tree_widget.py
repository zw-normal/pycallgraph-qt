from typing import Optional

from PySide2.QtCore import Slot, QItemSelection
from PySide2.QtWidgets import QTreeView, QWidget

from left_widget.tree_model import FunctionDefTreeModel
from domain.function_call_graph import GraphThread
from signal_hub import signalHub


class FunctionDefTreeWidget(QTreeView):

    def __init__(self, parent: Optional[QWidget] = ...):
        super().__init__(parent)
        self.graph_thread = None

        self.setModel(FunctionDefTreeModel(self))
        self.setHeaderHidden(True)

        self.model().functionItemsChanged.connect(
            self.functionItemsChanged)
        self.selectionModel().selectionChanged.connect(
            self.functionItemSelected)
        signalHub.exitingApp.connect(self.exitApp)

    @Slot(QItemSelection, QItemSelection)
    def functionItemSelected(
            self, selected: QItemSelection, deselected: QItemSelection):
        func_def = selected[0].indexes()[0].internalPointer()
        if func_def.function is not None:
            if self.graph_thread:
                self.graph_thread.resultReady.disconnect()
                self.graph_thread.stop()
            self.graph_thread = GraphThread(func_def.function.id)
            self.graph_thread.resultReady.connect(signalHub.getFuncCallDone)
            self.graph_thread.start()

    @Slot(int)
    def functionItemsChanged(self, func_count):
        if 0 < func_count < 6:
            self.expandAll()

    @Slot()
    def exitApp(self):
        if self.graph_thread:
            self.graph_thread.resultReady.disconnect()
            self.graph_thread.stop()
            self.graph_thread = None
