from sqlalchemy.orm import Session
from PySide2.QtCore import QThread, QMutex, Signal, QMutexLocker
import networkx as nx

from .function_query import (
    get_function, get_function_direct_calls)
from .function_uncertain import FunctionUncertain, FunctionUncertainType
from signal_hub import signalHub
from db import db_engine
from settings import settings


FunctionNodeColor = {
    1: 'wheat',
    2: 'yellow',
    3: 'orchid',
    4: 'bisque',
    5: 'lightskyblue',
    6: 'lightgray'
}


class GraphThread(QThread):

    resultReady = Signal(str)

    def __init__(self, func_id, parent=None):
        super().__init__(parent)
        self.func_id = func_id
        self.call_graph = nx.DiGraph()

        self.mutex = QMutex()
        self._abort = False

    @property
    def abort(self):
        with QMutexLocker(self.mutex):
            return self._abort

    def run(self) -> None:
        result = self._get_function_call_dot()
        if result:
            self.resultReady.emit(result)

    def stop(self):
        with QMutexLocker(self.mutex):
            self._abort = True
        self.wait()

    def _get_function_call_dot(self):
        assert db_engine.engine is not None
        with Session(db_engine.engine) as session:
            func_root = get_function(session, self.func_id)

            if func_root:
                # Find callers
                func_stack = self._record_unique_calls(session, func_root, True)
                self._record_ambiguity_calls(session, func_stack, True)

                # Find callees
                func_stack = self._record_unique_calls(session, func_root, False)
                self._record_ambiguity_calls(session, func_stack, False)
            else:
                return ''

        if not self.abort:
            signalHub.funcCallDotProgress.emit(
                'Rendering {} nodes'.format(len(self.call_graph.nodes())))

        return str(nx.nx_pydot.to_pydot(self.call_graph)) if not self.abort else ''

    def _add_function_node(self, func_node, is_root=False):
        if isinstance(func_node, FunctionUncertain):
            self.call_graph.add_node(
                func_node,
                label='{}\nUncertain'.format(
                    func_node.func_name),
                style='fill: lightcoral')
        else:
            self.call_graph.add_node(
                func_node,
                label='{}\n{} L{}'.format(
                    func_node.func_name,
                    func_node.base_source_name,
                    func_node.line_no),
                style='fill: {}'.format(
                    'lightgreen' if is_root else
                    FunctionNodeColor[func_node.func_type.value]))

    def _add_function_call(self, func_caller, func_callee, line_no=0):
        if line_no:
            self.call_graph.add_edge(
                func_caller, func_callee,
                label='L{}'.format(line_no))
        else:
            self.call_graph.add_edge(
                func_caller, func_callee
            )

    def _record_unique_calls(self, session, func_root, upstream):
        if not self.abort:
            func_stack = [func_root]
            max_func_nodes = settings.get_max_unique_nodes(upstream)

            for func_index, func_node in enumerate(func_stack):
                if self.abort:
                    break

                signalHub.funcCallDotProgress.emit(
                    'Adding {} {} (max: {})'.format(
                        func_index + 1,
                        'callers' if upstream else 'callees',
                        settings.get_max_unique_nodes(upstream)))
                self._add_function_node(func_node, func_node == func_root)

                func_calls = get_function_direct_calls(session, func_node.id, upstream)
                for func_call_info in func_calls:
                    func_call, line_no = func_call_info
                    if self.abort:
                        break
                    self._add_function_node(func_call)
                    if upstream:
                        self._add_function_call(func_call, func_node, line_no)
                    else:
                        self._add_function_call(func_node, func_call, line_no)
                    if func_call not in func_stack:
                        max_func_nodes = max_func_nodes - 1
                        func_stack.append(func_call)
                    if max_func_nodes <= 0:
                        return func_stack
            return func_stack
        return []

    def _record_ambiguity_calls(self, session, func_stack, upstream):
        if not self.abort:
            func_nodes_added = 0
            for func_index, func_node in enumerate(func_stack):
                if self.abort:
                    break

                signalHub.funcCallDotProgress.emit(
                    'Adding ambiguity {} for {} {}'.format(
                        'callers' if upstream else 'callees',
                        func_index + 1,
                        'callers' if upstream else 'callees',
                    ))

                func_calls = get_function_direct_calls(
                    session, func_node.id, upstream, exact_call=False)
                func_names = set((f[0].func_name for f in func_calls))
                for func_name in func_names:
                    if self.abort:
                        break
                    func_call = FunctionUncertain(
                        func_name,
                        FunctionUncertainType.Caller if upstream else FunctionUncertainType.Callee,
                        func_node.id)
                    self._add_function_node(func_call)
                    if upstream:
                        self._add_function_call(func_call, func_node)
                        func_nodes_added = func_nodes_added + 1
                        if func_nodes_added >= settings.max_uncertain_caller_nodes:
                            return
                    else:
                        self._add_function_call(func_node, func_call)
