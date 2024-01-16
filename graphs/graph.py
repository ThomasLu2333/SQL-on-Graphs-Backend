from datatypes.vertex import *
from datatypes.edge import *
from datatypes.primitive import *
from constraints.graphwide import *
from statuses.status import *


class GraphEdgesFromStatus(LeafStatus):
    def __init__(self, id: Primitive, graph_name: str, data: Optional[list[dict[str, Primitive]]] = None):
        super().__init__("Fetching Edges Successful",
                         "Fetching Edges Failed -- id doesn't exist",
                         data is not None,
                         {"id": id, "Graph Name": graph_name})


class GraphMutatorStatus(DerivedStatus):
    def __init__(self, substatuses: list[Status], graph_name: str):
        super().__init__("Graph Successfully Changed",
                         "Unable to Change Graph -- Changes Rolled Back",
                         substatuses,
                         {"Graph Name": graph_name})


class GraphCheckConstraintStatus(DerivedStatus):
    def __init__(self, substatuses: list[Status], graph_name: str):
        super().__init__("Graphwide Constraints Passed",
                         "Graphwide Constraints Violated",
                         substatuses,
                         {"Graph Name": graph_name})


class Graph:
    """
    A SQLonGraphs Graph, implemented using an adjacency matrix.
    Attributes:
        name: the string name of the graph.
        vertices: the Data object containing the VertexType of the graph.
        edges: the Data object containing the EdgeType of the graph. In addition, the from and to attribute of every entry
            in the EdgeType must correspond to a valid id in the above VertexType so that self.check_constraints()
            doesn't return a Statuses containing errors.
        M: an adjacency matrix representing the graph. M[id] is the list of edges incident from the vertex with id 'id'.
        constraints: a list of GraphwideConstraints imposed on this graph. They must be satisfied so that
            self.check_constraints() doesn't return a Statuses containing errors.
    """

    def __init__(self, name: str, vertextype: VertexType, edgetype: EdgeType, constraints: list[GraphwideConstraint]):
        """
        Creates a graph with no vertices or edges and with the given VertexType, EdgeType, and GraphwideConstraints.
        Client should call self.check_constraints() immediately after constructor call to detect any ill-formed Graphs.
        """
        self.name: str = name
        self.vertices: Data = Data(vertextype)
        self.edges: Data = Data(edgetype)
        self.constraints: list[GraphwideConstraint] = constraints
        self.constraints.append(GRAPHWIDE_CONSTRAINTS["REFERENTIAL_INTEGRITY"])
        self.M: dict[Primitive, list[dict[str, Primitive]]] = {}

    def vertices_list(self) -> list[dict[str, Primitive]]:
        """
        Return a list of all entries in the graph's VertexType.
        """
        return list(self.vertices.entries.values())

    def edges_list(self) -> list[dict[str, Primitive]]:
        """
        Return a list of all entries (edges) in the graph's EdgeType.
        """
        return list(self.edges.entries.values())

    def edges_from(self, id: Primitive) -> Status:
        """
        Return an OK Status object containing a list of edges in the context "data" where the 'from' attributes of the entries
        equal to 'id'. If 'id' doesn't exist, then an ERROR Status is returned.
        """
        return GraphEdgesFromStatus(id, self.name, self.M.get(id))

    def has_edge(self, start: Primitive, end: Primitive) -> bool:
        """
        Return whether there exists an edge with the from and to attribute equalling to 'start' and 'end' respectively.
        """
        if self.M.get(start) is None:
            return False
        for edge in self.M.get(start):
            if edge["to"] == end:
                return True
        return False

    def insert(self, new_vertices: Optional[list[dict[str, Primitive]]] = None,
               new_edges: Optional[list[dict[str, Primitive]]] = None) -> Status:
        """
        Insert a list of vertices into the VertexType of the graph and insert a list of edges into the EdgeType of
        the graph. If self.check_constraints() returns no ERRORs after the insertion, then a Statuses object with no ERRORs
        is returned. Otherwise, the insertion is rolled back with no state changed and ERROR statuses will be thrown.
        :param new_vertices:
        :param new_edges:
        :return: a Status showing the result of this operation.
        """
        new_vertices = [] if new_vertices is None else new_vertices
        new_edges = [] if new_edges is None else new_edges
        add_vertex_status = self.vertices.add_entries(new_vertices)
        add_edge_status = self.edges.add_entries(new_edges)
        graph_constraints_status = self.check_constraints()
        status = GraphMutatorStatus([add_vertex_status, add_edge_status, graph_constraints_status],
                                    self.name)
        if not status.success:
            self.vertices.rollback(new_vertices)
            self.edges.rollback(new_edges)
        else:
            for vertex in new_vertices:
                self.M[vertex["id"]] = []
            for edge in new_edges:
                self.M[edge["from"]].append(edge)
        return status

    def check_constraints(self) -> Status:
        """
        Checks whether the graphwide constraints of this graph is satisfied. If so, then an OK Status is returned.
        Otherwise, an ERROR is returned.
        """
        statuses = []
        for constraint in self.constraints:
            statuses.append(constraint.check(self.vertices, self.edges))
        return GraphCheckConstraintStatus(statuses, self.name)
