import pytest
from statuses.status import *


def test_leaf_status():
    A = LeafStatus("","Typewide Constraint Violated",False,
                   {"Constraint Name": "UNIQUE", "fields": ["id", "from", "to"]})
    assert not A.success
    print("\n")
    print(A)

def test_nonleaf_status():
    A = LeafStatus("","Typewide Constraint Violated", False,
                   {"Constraint Name": "UNIQUE", "fields": ["id", "from", "to"]})
    B = LeafStatus("","Typewide Constraint Violated", False,
                   {"Constraint Name": "NOTNULL", "fields": ["id"]})
    C = LeafStatus("Typewide Constraint Passed", "",True,
                   {"Constraint Name": "CHECK a > 1", "fields": ["a"]})
    D = DerivedStatus("Validation passed in a Vertex Type or Edge Type",
                      "Validation failed in a Vertex Type or Edge Type",
                      [A, B, C],
                      {"Type Name": "MyType"})
    E = LeafStatus("","Graphwide Constraint Violated", False,
                   {"Constraint Name": "UNDIRECTED"})
    E2 = LeafStatus("Graphwide Constraint Passed", "",True,
                   {"Constraint Name": "DIRECTED"})
    F = DerivedStatus("INSERT statement successful",
                      "INSERT statement FAILED",
                      [D, E, E2],
                      {"Graph Name": "MyGraph", "Lineno":11})
    assert not D.success
    assert not F.success
    print()
    print(F)