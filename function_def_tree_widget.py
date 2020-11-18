from typing import Optional

from PySide2.QtWidgets import QTreeView, QWidget

from function_def_tree_model import FunctionDefTreeModel

class FunctionDefTreeWidget(QTreeView):

    def __init__(self, parent: Optional[QWidget] = ...):
        super().__init__(parent)
        self.setModel(FunctionDefTreeModel(self))
        self.setHeaderHidden(True)
