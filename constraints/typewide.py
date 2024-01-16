from typing import Callable
from datatypes.primitive import *
from statuses.status import *


class TypewideConstraintCheckStatus(LeafStatus):
    def __init__(self, constraint_name: str, success: bool):
        super().__init__("Typewide Constraint Satisfied",
                         "Typewide Constraint Check Violated",
                         success,
                         {"Constraint Name": constraint_name})


class TypewideConstraint:
    """
    A constraint to be imposed on a VertexType or EdgeType object after binding.
    Attributes:
        name: the name of the Typewide Constraint.
        f : a function that takes a list of one or more lists of primitive-type values of the same lengths as arguments
            and returns a boolean value indicating whether the constraint has been preserved.
        is_local: indicates when changes are made to a set of values, whether the return value of f on the set of
            values depend on the portion of the values that are changed and not the entire new set of values.
    """

    def __init__(self, name: str, f: Callable[[list[list[Primitive]]], bool], is_local: bool):
        """
        Initializes a TypewideConstraint with a given name and f (see class invariant for the precondition on f).
        """
        self.name = name
        self.f = f
        self.is_local = is_local

    def check(self, values: list[list[Primitive]]) -> Status:
        """
        Checks whether the constraint is preserved on the given values.
        :return: a Status representing the result of this check
        """
        return TypewideConstraintCheckStatus(self.name, self.f(values))


def multicolumn(f: Callable[[list[Primitive]], bool]):
    """
    A decorator that converts a function f taking in a single column to a function accepting multiple columns and
    returns true if and only if f returns true on all columns.
    """

    def multicolumn_f(param: list[list[Primitive]]):
        for values in param:
            if not f(values):
                return False
        return True

    return multicolumn_f


@multicolumn
def NOTNULL_f(values: list[Primitive]):
    """
    Returns True if NULL isn't contained in values and False otherwise
    """
    return NULL not in values


@multicolumn
def UNIQUE_f(values: list[Primitive]):
    """
     Returns True if every value in values is unique and False otherwise
    """
    return len(list(set(values))) == len(values)


def get_CHECKTYPE_f(checked_type: PrimitiveTypes) -> Callable[[list[list[Primitive]]], bool]:
    """
    Create an f in a TypewideConstraint that checks whether the values in a list of columns are all of a specific type.
    """

    def CHECK_TYPE_f(values: list[Primitive]):
        for value in values:
            if value is not NULL and type(value) != checked_type:
                return False
        return True

    return multicolumn(CHECK_TYPE_f)


_TYPEWIDE_CONSTRAINTS = [
    TypewideConstraint("NOTNULL", NOTNULL_f, True),
    TypewideConstraint("UNIQUE", UNIQUE_f, False),
    TypewideConstraint("CHECKTYPE_INT", get_CHECKTYPE_f(PrimitiveTypes.INT.value), True),
    TypewideConstraint("CHECKTYPE_FLOAT", get_CHECKTYPE_f(PrimitiveTypes.FLOAT.value), True),
    TypewideConstraint("CHECKTYPE_BOOL", get_CHECKTYPE_f(PrimitiveTypes.BOOL.value), True),
    TypewideConstraint("CHECKTYPE_STR", get_CHECKTYPE_f(PrimitiveTypes.STR.value), True)
]

TYPEWIDE_CONSTRAINTS: dict[str, TypewideConstraint] = {constraint.name: constraint for constraint in
                                                       _TYPEWIDE_CONSTRAINTS}


def BoundTypewideConstraintStatusWrapper(status: Status, names: list[str]):
    status["Constraint Imposed On Fields"] = names
    return status


class BoundTypewideConstraint:
    """
    A TypewideConstraint bounded to one or more field names to enable mapping-based parameter passing.
    Attributes:
        constraint: a TypewideConstraint.
        names: a dictionary mapping field name to the position in the tuple passed into the constraint where
            the values of the field with this name will be called.
    """

    def __init__(self, constraint: TypewideConstraint, names: list[str]):
        """
        Initializes a BoundTypewideConstraint with the given constraint and field name mapping.
        """
        self.constraint = constraint
        self.names = names

    def check(self, values: dict[str, list[Primitive]]) -> Status:
        param = list(map(lambda x: values[x], self.names))
        return BoundTypewideConstraintStatusWrapper(self.constraint.check(param), list(self.names))
