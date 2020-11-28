import enum
import uuid


class FunctionUncertainType(enum.Enum):
    Caller = 1
    Callee = 2


class FunctionUncertain:

    def __init__(self, func_name, func_type, source_func_id):
        self.id = uuid.uuid4()
        self.func_name = func_name
        self.func_type = func_type
        self.source_func_id = source_func_id

    def __eq__(self, other):
        if isinstance(other, FunctionUncertain):
            return (self.func_name == other.func_name) and \
                   (self.func_type == other.func_type) and \
                   (self.source_func_id == other.source_func_id)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.func_name, self.func_type, self.source_func_id))

    def __repr__(self):
        return str(self.id)
