import enum
from typing import Optional, Any

from sqlalchemy.orm import Session
from PySide2.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt, Slot, QThread, Signal, QMutex

from db import db_engine
from domain.function_def import FunctionNode, FunctionNodeType
from domain.function_query import get_functions_by_name
from signal_hub import signalHub


class FunctionDefItemType(enum.Enum):
    Module = 1
    Class = 2
    Function = 3


class FunctionDefItem:

    def __init__(
            self, title: str, item_type: FunctionDefItemType,
            function: FunctionNode=None, parent=None):
        self.title = title
        self.type = item_type
        self.function = function
        self.parent = parent
        self.children = []

    def appendChild(self, item):
        try:
            index = self.children.index(item)
            return self.children[index]
        except ValueError:
            self.children.append(item)
            return item

    def child(self, row: int):
        return self.children[row]

    def rowCount(self):
        return len(self.children)

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0

    def __eq__(self, other):
        if isinstance(other, FunctionDefItem):
            return (self.title == other.title) and \
                   (self.type == other.type) and \
                   (self.function == other.function)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.title, self.type, self.function))


class FunctionDefTreeModelThread(QThread):

    resultReady = Signal(object)

    def __init__(self, func_name, parent=None):
        super().__init__(parent)
        self.func_name = func_name

        self.mutex = QMutex()
        self.abort = False

    def run(self) -> None:
        with Session(db_engine.engine) as session:
            root_item = FunctionDefItem(
                title='Root', item_type=FunctionDefItemType.Module)
            for function in get_functions_by_name(session, self.func_name):
                if self.abort:
                    self.resultReady.emit(None)
                signalHub.showStatusBarMessage.emit(
                    'Loading {}...'.format(function.full_name))
                next_parent = root_item
                modules = function.module_name.split('.')
                for module in modules:
                    if self.abort:
                        self.resultReady.emit(None)
                    module_item = FunctionDefItem(
                        title=module,
                        item_type=FunctionDefItemType.Module,
                        parent=next_parent)
                    next_parent = next_parent.appendChild(module_item)
                if function.class_name:
                    class_item = FunctionDefItem(
                        title=function.class_name,
                        item_type=FunctionDefItemType.Class,
                        parent=next_parent)
                    next_parent = next_parent.appendChild(class_item)
                function_item = FunctionDefItem(
                    title=function.func_name if function.func_type != FunctionNodeType.Class else '__init__',
                    item_type=FunctionDefItemType.Function,
                    function=function,
                    parent=next_parent)
                next_parent.appendChild(function_item)
            self.resultReady.emit(root_item)

    def stop(self):
        self.mutex.lock()
        self.abort = True
        self.mutex.unlock()

        self.wait()


class FunctionDefTreeModel(QAbstractItemModel):

    def __init__(self, parent: Optional[QObject]=...):
        super().__init__(parent)
        self.rootItem = FunctionDefItem(
            title='Root', item_type=FunctionDefItemType.Module)
        self.loadThread = None
        # self.loadFunctionItems('')

        signalHub.filterFuncDefTree.connect(self.loadFunctionItems)
        signalHub.dataFileOpened.connect(self.loadNewDataFile)
        signalHub.exitingApp.connect(self.exitApp)

    def rowCount(self, parent: QModelIndex=...) -> int:
        if not parent.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parent.internalPointer()

        return parent_item.rowCount()

    def columnCount(self, parent: QModelIndex=...) -> int:
        return 1

    def index(self, row: int, column: int, parent: QModelIndex=...) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def data(self, index: QModelIndex, role: int=...) -> Any:
        if not index.isValid():
            return None
        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()
        return item.title

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent

        if parent_item == self.rootItem:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    @Slot()
    def loadNewDataFile(self):
        self.loadFunctionItems('')

    @Slot(str)
    def loadFunctionItems(self, func_name):
        if self.loadThread:
            self.loadThread.resultReady.disconnect()
            self.loadThread.stop()
        signalHub.showStatusBarMessage.emit('Loading...')
        self.loadThread = FunctionDefTreeModelThread(func_name)
        self.loadThread.resultReady.connect(self.loadFunctionItemDone)
        self.loadThread.start()

    @Slot(object)
    def loadFunctionItemDone(self, root_item):
        if root_item:
            self.beginResetModel()
            self.rootItem = root_item
            self.endResetModel()
        signalHub.showStatusBarMessage.emit('Ready')

    @Slot()
    def exitApp(self):
        if self.loadThread:
            self.loadThread.resultReady.disconnect()
            self.loadThread.stop()
            self.loadThread = None
