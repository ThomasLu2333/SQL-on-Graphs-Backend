import pytest
from constraints.typewide import *


def test_NOTNULL():
    values1 = [['1', '2', '3', '4'], [1, 2, 3, 4], [None, True, False, False]]
    assert not NOTNULL_f(values1)
    values2 = [[1.2, 1.3, 1.4], ['A', "B", "C10101"]]
    assert NOTNULL_f(values2)
    print("\n" + str(TYPEWIDE_CONSTRAINTS["NOTNULL"].check(values1)))
    print("\n" + str(TYPEWIDE_CONSTRAINTS["NOTNULL"].check(values2)))
    bounded = BoundTypewideConstraint(TYPEWIDE_CONSTRAINTS["NOTNULL"], ["A", "B", "C"])
    bounded2 = BoundTypewideConstraint(TYPEWIDE_CONSTRAINTS["NOTNULL"], ["A", "B"])
    print("\n" + str(bounded.check(dict(zip(["A", "B", "C"], values1)))))
    print("\n" + str(bounded2.check(dict(zip(["A", "B"], values2)))))

def test_UNIQUE():
    values1 = [['1', '2', '3', '4'], [1, 2, 3, 4], [False, True, False, False]]
    assert not UNIQUE_f(values1)
    values2 = [[1.2, 1.3, 1.3], ['A', "B", "C10101"]]
    assert not UNIQUE_f(values2)
    values3 = [[1.2, 1.3, 1.4]]
    assert UNIQUE_f(values3)
    print("\n" + str(TYPEWIDE_CONSTRAINTS["UNIQUE"].check(values1)))
    print("\n" + str(TYPEWIDE_CONSTRAINTS["UNIQUE"].check(values3)))

def test_CHECKTYPE():
    values1 = [['1', '2', '3', None]]
    assert TYPEWIDE_CONSTRAINTS["CHECKTYPE_STR"].check(values1).success
    values2 = [[1.1, 1.2, 1.3, 1.4], [1.2, 1.1, 1.2, None]]
    assert TYPEWIDE_CONSTRAINTS["CHECKTYPE_FLOAT"].check(values2).success
    values3 = [[101, 102, "1", "2", 105], [101, 102, 107, 102, 105]]
    assert not TYPEWIDE_CONSTRAINTS["CHECKTYPE_INT"].check(values3).success
    values4 = [[True, False, None], [1, 0, False]]
    assert not TYPEWIDE_CONSTRAINTS["CHECKTYPE_BOOL"].check(values4).success

def test_BoundTypewideConstraint():
    bound_constraint = BoundTypewideConstraint(TYPEWIDE_CONSTRAINTS["UNIQUE"], ["column1", "column2"])
    assert not bound_constraint.check({"column1": ["a", "b", "c", "d"], "column2":["aa", "aa", "bb", "dd"]}).success
    print("\n" + str(bound_constraint.check({"column1": ["a", "b", "c", "d"], "column2":["aa", "aa", "bb", "dd"]})))
    bound_constraint = BoundTypewideConstraint(TYPEWIDE_CONSTRAINTS["CHECKTYPE_INT"], ["column1", "column2"])
    assert bound_constraint.check({"column1": [1, 100000, -999, 92382973], "column2": [1, 0, 3, 13]}).success
    print("\n" + str(bound_constraint.check({"column1": [1, 100000, -999, 92382973], "column2": [1, 0, 3, 13]})))