from typing import Callable
from datatypes.edge import EdgeType, FROM, TO, WEIGHT
from datatypes.primitive import INT, FLOAT
from datatypes.raw import ID
from datatypes.vertex import VertexType
from graphs.adjacency_matrix import Matrix
from graphs.data import Data
from statuses.status import *
from queue import Queue


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
    """
    Checks if the graph is a directed graph. Automatically True.
    """
    return True


def REFERENTIAL_INTEGRITY_f(vertices: Data, edges: Data):
    """
    Checks whether every edge in edges refers to two valid vertices in vertices.
    """
    for value in edges.values[FROM]:
        if value not in vertices.values[ID]:
            return False
    for value in edges.values[TO]:
        if value not in vertices.values[ID]:
            return False
    return True


def UNDIRECTED_f(vertices: Data, edges: Data):
    """
    Checks if every edge has a corresponding reversed edge.
    """
    # TODO: Make this more efficient by using an adjacency matrix
    for entry1 in edges.entries.values():
        flag = False
        for entry2 in edges.entries.values():
            if entry2[FROM] == entry1[TO] and entry2[TO] == entry1[FROM]:
                flag = True
                break
        if not flag:
            return False
        return True


def SIMPLE_f(vertices: Data, edges: Data):
    """
    Checks if the graph contains no self-loops and duplicate edges.
    """
    mat = Matrix(vertices, edges)
    for vid in vertices.ids:
        neighbors = [neighbor["id"] for neighbor in mat.get_neighbors(vid)]
        if vid in neighbors or len(neighbors)  == len(set(neighbors)):
            return False
    return True


def WEIGHTED_f(vertices: Data, edges: Data):
    """
    Checks if the graph has an attribute named weight with type INT or FLOAT
    """
    return (WEIGHT in edges.datatype.names and
            (edges.datatype.types[WEIGHT] == INT or edges.datatype.types[WEIGHT] == FLOAT))


def UNWEIGHTED_f(vertices: Data, edges: Data):
    """
    Checks if the graph doesn't have an attribute named weight.
    """
    return WEIGHT not in edges.datatype.names

def CONNECTED_f(vertices: Data, edges: Data):
    """
    Checks if the graph is undirected and every vertex is reachable from any other vertex.
    """
    if not UNDIRECTED_f(vertices, edges):
        return False
    visited = {idv: False for idv in vertices.ids}
    mat = Matrix(vertices, edges)
    queue = Queue()
    queue.put(vertices.ids[0])
    while not queue.empty():
        top = queue.get()
        neighbors = [neighbor["id"] for neighbor in mat.get_neighbors(top)]
        for neighbor in neighbors:
            if not visited[neighbor]:
                queue.put(neighbor)
                visited[neighbor] = True
    return False in visited.values()


def ACYCLIC_f(vertices: Data, edges: Data):
    """
    Checks if the graph doesn't contain any cycles.
    """
    return False


def TREE_f(vertices: Data, edges: Data):
    """
    Checks if the graph is connected and has one less edges than the number of vertices
    """
    return False


def COMPLETE_f(vertices: Data, edges: Data):
    """

    """
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
