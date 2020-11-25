import json

from sqlalchemy.orm import Session
from PySide2.QtCore import QObject, Signal, Slot

from function_query import get_function_callers_dot
from db import engine


class SignalHub(QObject):

    funcDefTreeFuncSel = Signal(int)
    funcCallersDotGet = Signal(str)

    @Slot(int)
    def getFuncCallersDot(self, func_id: int):
        with Session(engine) as session:
            self.funcCallersDotGet.emit(
                get_function_callers_dot(session, func_id))


signalHub = SignalHub()
