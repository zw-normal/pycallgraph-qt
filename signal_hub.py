from PySide2.QtWidgets import QMessageBox
from PySide2.QtCore import Qt, QObject, Signal, Slot
from sqlalchemy.orm import Session

from function_query import get_function
from db import engine


class SignalHub(QObject):

    filterFuncDefTree = Signal(str)

    funcCallDotProgress = Signal(str)
    funcCallDotGet = Signal(str)

    def __init__(self):
        super().__init__()

    @Slot(str)
    def getFuncCallDone(self, func_call_dot):
        self.funcCallDotGet.emit(func_call_dot)

    @Slot(str)
    def funcCallDotNodeSel(self, func_id):
        try:
            with Session(engine) as session:
                fund_id = int(func_id)
                func_def = get_function(session, func_id)

                msg_box = QMessageBox()
                msg_box.setText(
                    '<b>Source File:</b> <br>{}<br>'
                    '<b>Module Name:</b> {}<br>'
                    '<b>Function Name:</b> {}<br>'
                    '<b>Line No:</b> {}'.format(
                        func_def.source_file,
                        func_def.module_name,
                        func_def.func_name,
                        func_def.line_no));
                msg_box.setTextInteractionFlags(Qt.TextSelectableByMouse)
                msg_box.exec()
        except ValueError:
            pass


signalHub = SignalHub()
