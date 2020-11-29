from PySide2.QtCore import QSettings, Slot
from PySide2.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QFormLayout


class Settings:

    def __init__(self):
        self.settings = QSettings()
        self.settings = QSettings('settings.ini', QSettings.IniFormat)

    @property
    def max_unique_caller_nodes(self):
        return self.settings.value('max_unique_caller_nodes', 60)

    @max_unique_caller_nodes.setter
    def max_unique_caller_nodes(self, value: int):
        self.settings.setValue('max_unique_caller_nodes', value)

    @property
    def max_uncertain_caller_nodes(self):
        return self.settings.value('max_uncertain_caller_nodes', 60)

    @max_uncertain_caller_nodes.setter
    def max_uncertain_caller_nodes(self, value: int):
        self.settings.setValue('max_uncertain_caller_nodes', value)

    @property
    def max_unique_callee_nodes(self):
        return self.settings.value('max_unique_callee_nodes', 60)

    @max_unique_callee_nodes.setter
    def max_unique_callee_nodes(self, value: int):
        self.settings.setValue('max_unique_callee_nodes', value)

    def get_max_unique_nodes(self, upstream: bool):
        if upstream:
            return self.max_unique_caller_nodes
        return self.max_unique_callee_nodes


settings = Settings()


class SettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')

        form_layout = QFormLayout()
        self.max_unique_callers_edit = QLineEdit()
        self.max_unique_callers_edit.setText(str(settings.max_unique_caller_nodes))
        form_layout.addRow('Max Unique Caller Nodes:', self.max_unique_callers_edit)

        self.max_uncertain_callers_edit = QLineEdit()
        self.max_uncertain_callers_label = QLabel('Max Uncertain Caller Nodes:')
        self.max_uncertain_callers_edit.setText(str(settings.max_uncertain_caller_nodes))
        form_layout.addRow('Max Uncertain Caller Nodes:', self.max_uncertain_callers_edit)

        self.max_unique_callees_edit = QLineEdit()
        self.max_unique_callees_label = QLabel('Max Unique Callee Nodes:')
        self.max_unique_callees_edit.setText(str(settings.max_unique_callee_nodes))
        form_layout.addRow('Max Unique Callee Nodes:', self.max_unique_callees_edit)

        self.ok_button = QPushButton('Ok')
        self.cancel_button = QPushButton('Cancel')

        button_layout = QHBoxLayout()
        self.ok_button.clicked.connect(self.saveSettings)
        self.cancel_button.clicked.connect(self.closeDialog)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    @Slot()
    def saveSettings(self):
        try:
            settings.max_unique_caller_nodes = int(
                self.max_unique_callers_edit.text())
            settings.max_uncertain_caller_nodes = int(
                self.max_uncertain_callers_edit.text())
            settings.max_unique_callee_nodes = int(
                self.max_unique_callees_edit.text())
        except ValueError:
            pass
        else:
            self.closeDialog()

    @Slot()
    def closeDialog(self):
        self.close()
