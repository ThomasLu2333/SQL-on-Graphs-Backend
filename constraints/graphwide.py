from typing import Callable
from datatypes.edge import EdgeType
from datatypes.vertex import VertexType
from graphs.data import Data
from statuses.status import *


class GraphwideConstraintCheckStatus(LeafStatus):
    def __init__(self, name: str, success: bool):
        super().__init__("Graphwide Constraint Satisfied",
                         "Graphwide Constraint Check Violated",
                         success,
                         {"Constraint Name": name})


class GraphwideConstraint:
    """
    A constraint imposed on a Graph object.
    Attributes:
        name: the name of the GraphwideConstraint
        f: a function that takes the vertices, edges, and M attributes of a Graph as parameters and a Status indicating
            whether the constraint has been satisfied.
    """

    def __init__(self, name: str, f: Callable[[Data, Data], bool]):
        """
        Initializes a GraphwideConstraint with a given name and f.
        """
        self.name = name
        self.f = f

    def check(self, vertices: Data, edges: Data) -> Status:
        """
        Checks whether f is satisfied with the given collection of vertices and edges. If they are both empty, then
            returns true regardless of values of f.
        :return: A Status object showing the result of this operation.
        """
        result = True if vertices.size() == 0 and edges.size() == 0 else self.f(vertices, edges)
        return GraphwideConstraintCheckStatus(self.name, result)


def DIRECTED_f(vertices: Data, edges: Data):
    return True

def REFERENTIAL_INTEGRITY_f(vertices: Data, edges: Data):
    return False

def UNDIRECTED_f(vertices: Data, edges: Data):
    return False


def SIMPLE_f(vertices: Data, edges: Data):
    return False


def WEIGHTED_f(vertices: Data, edges: Data):
    return False


def UNWEIGHTED_f(vertices: Data, edges: Data):
    return False


def CONNECTED_f(vertices: Data, edges: Data):
    return False


def ACYCLIC_f(vertices: Data, edges: Data):
    return False


def TREE_f(vertices: Data, edges: Data):
    return False


def COMPLETE_f(vertices: Data, edges: Data):
    return False


def BIPARTITE_f(vertices: Data, edges: Data):
    return False


_GRAPHWIDE_CONSTRAINTS = [
    GraphwideConstraint("DIRECTED", DIRECTED_f),
    GraphwideConstraint("REFERENTIAL_INTEGRITY", REFERENTIAL_INTEGRITY_f),
    GraphwideConstraint("UNDIRECTED", UNDIRECTED_f),
    GraphwideConstraint("SIMPLE", SIMPLE_f),
    GraphwideConstraint("WEIGHTED", WEIGHTED_f),
    GraphwideConstraint("UNWEIGHTED", UNWEIGHTED_f),
    GraphwideConstraint("CONNECTED", CONNECTED_f),
    GraphwideConstraint("ACYCLIC", ACYCLIC_f),
    GraphwideConstraint("TREE", TREE_f),
    GraphwideConstraint("COMPLETE", COMPLETE_f),
    GraphwideConstraint("BIPARTITE", BIPARTITE_f)
]

GRAPHWIDE_CONSTRAINTS: dict[str, GraphwideConstraint] = {constraint.name: constraint for constraint in
                                                         _GRAPHWIDE_CONSTRAINTS}
