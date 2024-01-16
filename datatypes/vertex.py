from typing import Optional
from datatypes.primitive import Primitive
from datatypes.raw import *
from statuses.old_status import Statuses

class VertexType(RawType):
    """
    A type for vertices of a Graph.
    """
    def check_constraints(self, values: dict[str, list[Primitive]],
                          deltas: dict[str, list[Primitive]] = None) -> Status:
        return VertexOrEdgeTypeCheckStatus(super()._check_constraints(values, deltas), self.name)


