from typing import List

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql.expression import true, false

from .function_def import FunctionNode
from .function_call import FunctionCall


def get_function(session, func_id: int):
    stmt = select(FunctionNode).where(FunctionNode.id == func_id)
    try:
        return session.execute(stmt).scalar_one()
    except NoResultFound:
        return None


def get_functions_by_name(session, func_name: str) -> List[FunctionNode]:
    if not func_name:
        stmt = select(FunctionNode).order_by(
            FunctionNode.module_name, FunctionNode.func_name)
    else:
        stmt = select(FunctionNode).where(
            FunctionNode.func_name == func_name).order_by(
            FunctionNode.module_name, FunctionNode.func_name)
    return session.execute(stmt).scalars()


def get_function_direct_calls(
        session, func_id: int, upstream: bool, exact_call: bool=True):
    if upstream:
        func_ids = (FunctionCall.caller_id, FunctionCall.callee_id)
    else:
        func_ids = (FunctionCall.callee_id, FunctionCall.caller_id)
    stmt = select(FunctionNode, FunctionCall.line_no).join(
        FunctionCall, onclause=FunctionNode.id == func_ids[0]).where(
        func_ids[1] == func_id,
        FunctionCall.exact_call == (true() if exact_call else false()),
    ).order_by(FunctionCall.line_no)
    return session.execute(stmt)
