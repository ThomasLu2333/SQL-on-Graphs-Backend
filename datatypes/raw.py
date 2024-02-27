from constraints.typewide import *
from datatypes.primitive import *
from statuses.status import *
from typing import Optional

ID: str = "id"

class VertexOrEdgeTypeMissingFieldStatus(LeafStatus):
    def __init__(self, field_name:str, type_name:str):
        super().__init__("",
                         f"Definition or Constraints Missing for Field {field_name} in a Vertex- or Edge type",
                         False,
                         {"Type Name":type_name})


class VertexOrEdgeTypeCheckStatus(DerivedStatus):
    def __init__(self, statuses : list[Status], type_name:str):
        super().__init__("Validation Passed in a Vertex- or Edge Type",
                         "Validation Failed in a Vertex- or Edge Type",
                         statuses,
                         {"Type Name":type_name})


class RawType(metaclass=ABCMeta):
    """
    The base class to be inherited by the VertexType and EdgeType class, both of which defines a list of fields
    for the entries contained in a Data object. Must not be instantiated directly.
    A field named 'id' with constraints UNIQUE and NOTNULL must be imposed so that self.check_constraints() don't return
    a Statuses containing errors.
    Attributes:
        name: a string name for this type.
        names: a list of strings as names of each field.
        types: a dictionary mapping each field name to a primitive datatype that the field has
        constraints: a list of BoundTypewideConstraints imposed on this type. They must be satisfied so that
            self.check_constraints() don't return a Statuses containing errors.
    """

    def __init__(self, name: str,
                 names: list[str],
                 types: dict[str, PrimitiveTypes],
                 constraints: list[BoundTypewideConstraint] = None):
        """
        Creates a RawType with ethe given names, types, and constraints.
        :param types: a dictionary mapping each name to a primitive datatype that the field has
        :param constraints: a dictionary mapping a TypewideConstraint to a list of field names that it will bind to.
        """
        self.constraints = [] if None else constraints
        self.name = name
        self.names = names
        self.types = types
        for field_name, datatype in types.items():
            type_constraint = TYPEWIDE_CONSTRAINTS["CHECKTYPE_" + datatype.name]
            self.constraints.append(BoundTypewideConstraint(type_constraint, [field_name]))

    def _check_constraints(self, values: dict[str, list[Primitive]],
                          deltas: dict[str, list[Primitive]] = None) -> list[Status]:
        """
        the internal helper for self.check_constraints(). Returns a list of Status objects instead of a Status.
        """
        statuses = []
        flagA = False
        flagB = False
        for bound_constraint in self.constraints:
            if ID in bound_constraint.names and bound_constraint.constraint is TYPEWIDE_CONSTRAINTS["UNIQUE"]:
                flagA = True
            if ID in bound_constraint.names and bound_constraint.constraint is TYPEWIDE_CONSTRAINTS["NOTNULL"]:
                flagB = True
            targets = deltas if deltas is not None and bound_constraint.constraint.is_local else values
            statuses.append(bound_constraint.check(targets))
        if not flagA or not flagB:
            statuses.append(VertexOrEdgeTypeMissingFieldStatus(ID, self.name))
        for bound_constraint in self.constraints:
            targets = deltas if deltas is not None and bound_constraint.constraint.is_local else values
            statuses.append(bound_constraint.check(targets))
        return statuses

    @abstractmethod
    def check_constraints(self, values: dict[str, list[Primitive]],
                          deltas: dict[str, list[Primitive]] = None) -> Status:
        """
        Checks whether the constraints are satisfied in the list of entries. When a Database is trying to
        create a new Vertex- or EdgeType, self.check_constraints() should be called after instantiation to detect
        any ill-created objects.
        :param values: the entire list of entries.
        :param deltas: the portion of the entries that are changed from an operation such as insertion or deletion.
        :return: a Status object showing result of this check.
        """
        pass
