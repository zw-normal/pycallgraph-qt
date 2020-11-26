from typing import List

from sqlalchemy import select
from sqlalchemy.sql.expression import true, false

from function_def import FunctionNode
from function_call import FunctionCall


def get_function(session, func_id):
    stmt = select(FunctionNode).where(FunctionNode.id == func_id)
    return session.execute(stmt).scalar_one()


def get_all_functions(session) -> List[FunctionNode]:
    stmt = select(FunctionNode).order_by(
        FunctionNode.module_name, FunctionNode.func_name)
    return session.execute(stmt).scalars().all()


def get_function_direct_calls(session, func_id: int, upstream, exact_call: bool=True):
    if upstream:
        func_ids = (FunctionCall.caller_id, FunctionCall.callee_id)
    else:
        func_ids = (FunctionCall.callee_id, FunctionCall.caller_id)
    stmt = select(FunctionNode).join(
        FunctionCall, onclause=FunctionNode.id == func_ids[0]).where(
        func_ids[1] == func_id,
        FunctionCall.exact_call == (true() if exact_call else false()),
    ).order_by(FunctionCall.line_no)
    return session.execute(stmt).scalars().all()
