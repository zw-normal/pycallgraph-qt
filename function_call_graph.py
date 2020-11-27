from sqlalchemy.orm import Session
from PySide2.QtCore import QThread, QMutex, Signal
import networkx as nx

from function_query import (
    get_function, get_function_direct_calls)
from function_ambiguity import FunctionAmbiguity, FunctionAmbiguityType
from setting import MAX_UNIQUE_CALLER_NODES, MAX_UNIQUE_CALLEE_NODES
from signal_hub import signalHub
from db import engine


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
        self.abort = False

    def run(self) -> None:
        result = self._get_function_call_dot()
        if result:
            self.resultReady.emit(result)

    def stop(self):
        self.mutex.lock()
        self.abort = True
        self.mutex.unlock()

        self.wait()

    def _get_function_call_dot(self):
        with Session(engine) as session:
            func_root = get_function(session, self.func_id)

            # Find callers
            self._record_unique_calls(session, func_root, True)
            # self._record_ambiguity_calls(session, func_stack, True)

            # Find callees
            func_stack = self._record_unique_calls(session, func_root, False)
            self._record_ambiguity_calls(session, func_stack, False)

        signalHub.funcCallDotProgress.emit(
            'Rendering {} nodes'.format(len(self.call_graph.nodes())))

        return str(nx.nx_pydot.to_pydot(self.call_graph)) if not self.abort else ''

    def _add_function_node(self, func_node, is_root=False):
        if isinstance(func_node, FunctionAmbiguity):
            self.call_graph.add_node(
                func_node,
                label='{}\nambiguity'.format(
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

    def _add_function_call(self, func_caller, func_callee):
        self.call_graph.add_edge(func_caller, func_callee)

    def _record_unique_calls(self, session, func_root, upstream):
        if not self.abort:
            func_stack = [func_root]
            max_func_nodes = MAX_UNIQUE_CALLER_NODES if upstream else MAX_UNIQUE_CALLEE_NODES

            for func_index, func_node in enumerate(func_stack):
                if self.abort:
                    break

                signalHub.funcCallDotProgress.emit(
                    'Adding {} {} (max: {})'.format(
                        func_index + 1,
                        'callers' if upstream else 'callees',
                        MAX_UNIQUE_CALLER_NODES if upstream else MAX_UNIQUE_CALLEE_NODES))
                self._add_function_node(func_node, func_node == func_root)

                func_calls = get_function_direct_calls(session, func_node.id, upstream)
                for func_call in func_calls:
                    if self.abort:
                        break
                    self._add_function_node(func_call)
                    if upstream:
                        self._add_function_call(func_call, func_node)
                    else:
                        self._add_function_call(func_node, func_call)
                    if func_call not in func_stack:
                        max_func_nodes = max_func_nodes - 1
                        func_stack.append(func_call)
                    if max_func_nodes <= 0:
                        return func_stack
            return func_stack
        return []

    def _record_ambiguity_calls(self, session, func_stack, upstream):
        if not self.abort:
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
                func_names = set((f.func_name for f in func_calls))
                for func_name in func_names:
                    if self.abort:
                        break
                    func_call = FunctionAmbiguity(
                        func_name,
                        FunctionAmbiguityType.Caller if upstream else FunctionAmbiguityType.Callee,
                        func_node.id)
                    self._add_function_node(func_call)
                    if upstream:
                        self._add_function_call(func_call, func_node)
                    else:
                        self._add_function_call(func_node, func_call)
