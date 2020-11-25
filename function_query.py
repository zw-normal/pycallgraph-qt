from typing import List

from sqlalchemy import select
from sqlalchemy.sql.expression import true
import networkx as nx

from function_def import FunctionNode
from function_call import FunctionCall


functionNodeColor = {
    1: 'wheat',
    2: 'yellow',
    3: 'orchid',
    4: 'bisque',
    5: 'lightskyblue',
    6: 'lightgray'
}

def get_all_functions(session) -> List[FunctionNode]:
    stmt = select(FunctionNode)
    return session.execute(stmt).scalars().all()


def get_function_direct_callers(
        session, func_id: int, only_exact_call: bool=True):
    stmt = select(FunctionNode).where(
        FunctionNode.id == FunctionCall.caller_id,
        FunctionCall.callee_id == func_id)
    if only_exact_call:
        stmt.where(FunctionCall.exact_call == true())
    return session.execute(stmt).scalars().all()


def add_function_node(digraph, func_node, is_root=False):
    digraph.add_node(
        func_node,
        label='{}\n{} L{}'.format(
            func_node.func_name,
            func_node.base_source_name,
            func_node.line_no),
        style='fill: {}'.format(
            'lightgreen' if is_root else
            functionNodeColor[func_node.func_type.value]))


def add_function_call(digraph, func_caller, func_callee):
    digraph.add_edge(func_caller, func_callee)


def get_function_callers_dot(session, func_id: int):
    call_graph = nx.DiGraph()
    func_stack = []

    stmt = select(FunctionNode).where(FunctionNode.id == func_id)
    func_root = session.execute(stmt).scalar_one()
    func_stack.append(func_root)

    for func_node in func_stack:
        add_function_node(call_graph, func_node, func_node == func_root)

        func_callers = get_function_direct_callers(session, func_node.id)
        for func_caller in func_callers:
            add_function_node(call_graph, func_caller)
            add_function_call(call_graph, func_caller, func_node)
            if func_caller not in func_stack:
                func_stack.append(func_caller)
    return str(nx.nx_pydot.to_pydot(call_graph))
