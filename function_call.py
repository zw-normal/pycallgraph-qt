from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from function_def import Base, FunctionNode


class FunctionCall(Base):

    __tablename__ = 'function_call'

    id = Column(Integer, primary_key=True)
    caller_id = Column(
        Integer, ForeignKey('function_node.id'), nullable=False, index=True)
    callee_id = Column(
        Integer, ForeignKey('function_node.id'), nullable=False, index=True)
    line_no = Column(Integer)
    exact_call = Column(Boolean, default=False, index=True)

    caller = relationship(FunctionNode, foreign_keys=[caller_id])
    callee = relationship(FunctionNode, foreign_keys=[callee_id])
