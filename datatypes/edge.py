from typing import Optional

from datatypes.primitive import Primitive
from datatypes.raw import *
from statuses.status import *
from constraints.typewide import *

FROM : str = "from"
TO: str = "to"
WEIGHT: str = "weight"

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
            if FROM in bound_constraint.names and bound_constraint.constraint is TYPEWIDE_CONSTRAINTS["NOTNULL"]:
                flag_from = True
            if TO in bound_constraint.names and bound_constraint.constraint is TYPEWIDE_CONSTRAINTS["NOTNULL"]:
                flag_to = True
        if not flag_from:
            statuses.append(VertexOrEdgeTypeMissingFieldStatus(FROM, self.name))
        if not flag_to:
            statuses.append(VertexOrEdgeTypeMissingFieldStatus(TO, self.name))
        statuses += super()._check_constraints(values, deltas)
        return VertexOrEdgeTypeCheckStatus(statuses, self.name)
