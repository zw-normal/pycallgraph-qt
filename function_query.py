from typing import List

from sqlalchemy import select
from sqlalchemy.sql.expression import true, false
import networkx as nx

from function_def import FunctionNode
from function_ambiguity import FunctionAmbiguity, FunctionAmbiguityType
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
    stmt = select(FunctionNode).order_by(
        FunctionNode.module_name, FunctionNode.func_name)
    return session.execute(stmt).scalars().all()


def get_function_direct_callers(
        session, func_id: int, exact_call: bool=True):
    stmt = select(FunctionNode).join(
        FunctionCall, onclause=FunctionNode.id == FunctionCall.caller_id).where(
        FunctionCall.callee_id == func_id,
        FunctionCall.exact_call == (true() if exact_call else false()),
    ).order_by(FunctionCall.line_no)
    return session.execute(stmt).scalars().all()


def get_function_direct_callees(
        session, func_id: int, exact_call: bool=True):
    stmt = select(FunctionNode).join(
        FunctionCall, onclause=FunctionNode.id == FunctionCall.callee_id).where(
        FunctionCall.caller_id == func_id,
        FunctionCall.exact_call == (true() if exact_call else false()),
    ).order_by(FunctionCall.line_no)
    return session.execute(stmt).scalars().all()


def add_function_node(digraph, func_node, is_root=False):
    if isinstance(func_node, FunctionAmbiguity):
        digraph.add_node(
            func_node,
            label='{}\nambiguity'.format(
                func_node.func_name),
            style='fill: lightcoral')
    else:
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

    stmt = select(FunctionNode).where(FunctionNode.id == func_id)
    func_root = session.execute(stmt).scalar_one()

    # Begin to find callers
    func_stack = [func_root]

    # Record unique callers of each level
    for func_node in func_stack:
        add_function_node(call_graph, func_node, func_node == func_root)

        func_callers = get_function_direct_callers(session, func_node.id)
        for func_caller in func_callers:
            add_function_node(call_graph, func_caller)
            add_function_call(call_graph, func_caller, func_node)
            if func_caller not in func_stack:
                func_stack.append(func_caller)

    # Record ambiguity callers of each level
    for func_node in func_stack:
        func_callers = get_function_direct_callers(
            session, func_node.id, exact_call=False)
        func_caller_names = set((f.func_name for f in func_callers))
        for func_caller_name in func_caller_names:
            func_caller = FunctionAmbiguity(
                func_caller_name,
                FunctionAmbiguityType.Caller,
                func_node.id)
            add_function_node(call_graph, func_caller)
            add_function_call(call_graph, func_caller, func_node)

    # Begin to find callees
    func_stack = [func_root]

    # Record unique callees of each level
    for func_node in func_stack:
        add_function_node(call_graph, func_node, func_node == func_root)

        func_callees = get_function_direct_callees(session, func_node.id)
        for func_callee in func_callees:
            add_function_node(call_graph, func_callee)
            add_function_call(call_graph, func_node, func_callee)
            if func_callee not in func_stack:
                func_stack.append(func_callee)

    # Record ambiguity callees of each level
    for func_node in func_stack:
        func_callees = get_function_direct_callees(
            session, func_node.id, exact_call=False)
        func_callee_names = set((f.func_name for f in func_callees))
        for func_callee_name in func_callee_names:
            func_callee = FunctionAmbiguity(
                func_callee_name,
                FunctionAmbiguityType.Callee,
                func_node.id)
            add_function_node(call_graph, func_callee)
            add_function_call(call_graph, func_node, func_callee)

    return str(nx.nx_pydot.to_pydot(call_graph))
