import enum

from sqlalchemy import Column, Integer, String, Enum, UniqueConstraint, select, Index
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class FunctionNodeType(enum.Enum):
    Normal = 1
    Class = 2
    Property = 3
    ClassMethod = 4
    StaticMethod = 5
    InstanceMethod = 6


class FunctionNode(Base):

    __tablename__ = 'function_node'

    id = Column(Integer, primary_key=True)
    source_file = Column(String)
    line_no = Column(Integer)
    col_offset = Column(Integer)

    module_name = Column(String)
    class_name = Column(String)
    func_type = Column(Enum(FunctionNodeType))
    func_name = Column(String, index=True)
    min_args = Column(Integer, index=True)
    max_args = Column(Integer, index=True)

    __table_args__ = (
        UniqueConstraint('source_file', 'line_no', 'col_offset', name='function_def_pos'),)

    def __eq__(self, other):
        if isinstance(other, FunctionNode):
            return (self.source_file == other.source_file) and \
                   (self.line_no == other.line_no) and \
                   (self.col_offset == other.col_offset)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.source_file, self.line_no, self.col_offset))
