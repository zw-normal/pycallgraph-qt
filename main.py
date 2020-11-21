import sys

from PySide2 import QtGui
from PySide2.QtCore import QUrl
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import (
    QHBoxLayout, QSizePolicy, QApplication,
    QMainWindow, QAction, QWidget)

from function_def_tree.tree_widget import FunctionDefTreeWidget
from function_call_plot.plot_widget import PlotWidget


class MainWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        # Creating left FunctionTreeWidget
        self.func_tree_widget = FunctionDefTreeWidget(self)

        # Creating right PlotWidget
        self.plot_widget = PlotWidget(self)

        # Main layout
        self.main_layout = QHBoxLayout()

        # Left layout
        self.main_layout.addWidget(self.func_tree_widget)

        # Right layout
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(1)
        self.plot_widget.setSizePolicy(size)

        self.main_layout.addWidget(self.plot_widget)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('Python Code Graph')
        self.setCentralWidget(MainWidget())

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('File')

        # Exit QAction
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        self.file_menu.addAction(exit_action)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage('Data loaded')


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    geometry = QtGui.QGuiApplication.primaryScreen().availableGeometry()

    window = MainWindow()
    window.resize(
        int(geometry.width() * 0.8), int(geometry.height() * 0.7))
    window.show()

    # Execute application
    sys.exit(app.exec_())
