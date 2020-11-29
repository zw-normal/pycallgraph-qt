import sys

from PySide2 import QtGui
from PySide2.QtCore import Slot, Qt
from PySide2.QtGui import QKeySequence, QCloseEvent
from PySide2.QtWidgets import (
    QHBoxLayout, QSizePolicy, QApplication,
    QMainWindow, QAction, QWidget, QMessageBox, QFileDialog)
from sqlalchemy.orm import Session

from db import db_engine
from domain.function_query import get_function
from left_widget import LeftWidget
from right_widget import RightWidget
from settings import SettingsDialog
from signal_hub import signalHub


class MainWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.left_widget = LeftWidget(self)
        self.right_widget = RightWidget(self)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.left_widget)

        # Right layout
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(1)
        self.right_widget.setSizePolicy(size)

        main_layout.addWidget(self.right_widget)

        # Set the layout to the QWidget
        self.setLayout(main_layout)


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('Python Code Graph')
        self.setCentralWidget(MainWidget())

        # Menu
        self.menu = self.menuBar()
        self.menu.setNativeMenuBar(False)
        self.file_menu = self.menu.addMenu('File')

        # Open File Action
        open_file_action = QAction('Open...', self)
        open_file_action.triggered.connect(self.openDataFile)

        # Export Png Action
        export_png_action = QAction('Export PNG...', self)
        export_png_action.triggered.connect(self.exportPng)

        # Settings Action
        settings_action = QAction('Settings...', self)
        settings_action.triggered.connect(self.openSettings)

        # Exit QAction
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        # Add menu action
        self.file_menu.addAction(open_file_action)
        # self.file_menu.addAction(export_png_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(settings_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(exit_action)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage('Ready')

        # Signal Connection
        signalHub.showFuncDefMessageBox.connect(self.showFuncDefMessageBox)
        signalHub.showStatusBarMessage.connect(self.showStatusBarMessage)

    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
        signalHub.exitingApp.emit()

    @Slot()
    def openDataFile(self):
        file_name = QFileDialog.getOpenFileName(
            self, 'Open Data File', '', 'Data Files (*.sqlite3)')
        if file_name[0]:
            db_engine.openDataFile(file_name[0])
            signalHub.dataFileOpened.emit()

    @Slot()
    def exportPng(self):
        signalHub.funcCallDotSave.emit()

    @Slot()
    def openSettings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.show()

    @Slot(object)
    def showFuncDefMessageBox(self, func_id: object):
        assert db_engine.engine is not None
        try:
            if isinstance(func_id, str):
                func_id = int(func_id)
            with Session(db_engine.engine) as session:
                func_def = get_function(session, func_id)
                if func_def:
                    msg_box = QMessageBox()
                    msg_box.setText(
                        '<b>Source File:</b> <br>{}<br>'
                        '<b>Module Name:</b> {}<br>'
                        '<b>Function Name:</b> {}<br>'
                        '<b>Line No:</b> {}'.format(
                            func_def.source_file,
                            func_def.module_name,
                            func_def.func_name,
                            func_def.line_no))
                    msg_box.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    msg_box.exec()
        except ValueError:
            pass

    @Slot(str)
    def showStatusBarMessage(self, message: str):
        self.status.showMessage(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName('Datagraph Space')
    app.setOrganizationDomain('datagraph.space')
    app.setApplicationName('Python Call Graph')
    geometry = QtGui.QGuiApplication.primaryScreen().availableGeometry()

    window = MainWindow()
    window.resize(
        int(geometry.width() * 0.8), int(geometry.height() * 0.7))
    window.show()

    # Execute application
    sys.exit(app.exec_())
