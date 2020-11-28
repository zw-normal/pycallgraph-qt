from PySide2.QtWidgets import QWidget, QVBoxLayout
from left_widget.tree_widget import FunctionDefTreeWidget
from left_widget.tree_filter_edit import FunctionDefTreeFilterEdit


class LeftWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.func_tree_filter_edit = FunctionDefTreeFilterEdit(self)
        self.func_tree_widget = FunctionDefTreeWidget(self)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.func_tree_filter_edit)
        self.main_layout.addWidget(self.func_tree_widget)

        self.setLayout(self.main_layout)
