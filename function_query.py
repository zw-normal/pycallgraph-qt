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
    stmt = select(FunctionNode)
    return session.execute(stmt).scalars().all()


def get_function_direct_callers(
        session, func_id: int, exact_call: bool=True):
    stmt = select(FunctionNode).join(
        FunctionCall, onclause=FunctionNode.id == FunctionCall.caller_id).where(
        FunctionCall.callee_id == func_id,
        FunctionCall.exact_call == (true() if exact_call else false()),
    )
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

    # Record the ambiguity callers
    func_callers = get_function_direct_callers(
        session, func_root.id, exact_call=False)
    print(len(func_callers))
    func_caller_names = set((f.func_name for f in func_callers))
    for func_caller_name in func_caller_names:
        func_caller = FunctionAmbiguity(
            func_caller_name,
            FunctionAmbiguityType.Caller,
            func_root.id)
        add_function_node(call_graph, func_caller)
        add_function_call(call_graph, func_caller, func_root)

    return str(nx.nx_pydot.to_pydot(call_graph))
