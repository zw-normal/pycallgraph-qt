import enum
from typing import Optional, Any

from sqlalchemy.orm import Session
from PySide2.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt, Slot

from db import engine
from function_def import FunctionNode, FunctionNodeType
from function_query import get_functions_by_name
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


class FunctionDefTreeModel(QAbstractItemModel):

    def __init__(self, parent: Optional[QObject]=...):
        super().__init__(parent)
        self.rootItem = FunctionDefItem(
            title='Root', item_type=FunctionDefItemType.Module)
        self.loadFunctionItems('')
        signalHub.filterFuncDefTree.connect(self.loadFunctionItems)

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

    @Slot(str)
    def loadFunctionItems(self, func_name):
        self.beginResetModel()
        with Session(engine) as session:
            self.rootItem = FunctionDefItem(
                title='Root', item_type=FunctionDefItemType.Module)
            for function in get_functions_by_name(session, func_name):
                next_parent = self.rootItem
                modules = function.module_name.split('.')
                for module in modules:
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
        self.endResetModel()
