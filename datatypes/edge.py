from typing import Optional

from datatypes.primitive import Primitive
from datatypes.raw import *
from statuses.status import *
from constraints.typewide import *


class EdgeType(RawType):
    """
    A type for edges of a Graph.
    In addition to RawType's preconditions, a field named "from" with constraint NOTNULL and another field named
    "to" with constraint NOTNULL must be included in any EdgeType. Otherwise, a Statuses containing an error Status will
    be raised when calling check_constraints().
    """

    def check_constraints(self, values: dict[str, list[Primitive]],
                          deltas: dict[str, list[Primitive]] = None) -> Status:
        flag_from = flag_to = False
        statuses = []
        for bound_constraint in self.constraints:
            if "from" in bound_constraint.names and bound_constraint.constraint is TYPEWIDE_CONSTRAINTS["NOTNULL"]:
                flag_from = True
            if "to" in bound_constraint.names and bound_constraint.constraint is TYPEWIDE_CONSTRAINTS["NOTNULL"]:
                flag_to = True
        if not flag_from:
            statuses.append(VertexOrEdgeTypeMissingFieldStatus("from", self.name))
        if not flag_to:
            statuses.append(VertexOrEdgeTypeMissingFieldStatus("to", self.name))
        statuses += super()._check_constraints(values, deltas)
        return VertexOrEdgeTypeCheckStatus(statuses, self.name)
