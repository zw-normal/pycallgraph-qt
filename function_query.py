from typing import List

from sqlalchemy import select

from function_def import FunctionNode


def get_all_functions(session) -> List[FunctionNode]:
    stmt = select(FunctionNode)
    return session.execute(stmt).scalars().all()
