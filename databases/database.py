from typing import Optional

from constraints.graphwide import GraphwideConstraint
from constraints.typewide import TypewideConstraint, BoundTypewideConstraint
from datatypes.edge import EdgeType
from datatypes.primitive import PrimitiveTypes, Primitive
from datatypes.vertex import VertexType
from graphs.graph import Graph
from statuses.status import *


class DatabaseNameNoDuplicatesStatus(LeafStatus):
    def __init__(self, success: bool, name: str, lineno: int):
        super().__init__("New Name Confirmed",
                         "Duplicated Name Found for Another Database Object",
                         success,
                         {"name": name, "lineno": lineno})


class DatabaseNameExistsStatus(LeafStatus):
    def __init__(self, success: bool, name: str, lineno: int):
        super().__init__("Name for the Database Object Found",
                         "Duplicated Name Found for Another Database Object",
                         success,
                         {"name": name, "lineno": lineno})


class DatabaseOperationStatus(DerivedStatus):
    def __init__(self, opname: str, substatuses: list[Status], object_name: str, lineno: int):
        super().__init__(f"{opname} Successful",
                         f"{opname} Failed",
                         substatuses,
                         {"Object Name": object_name, "lineno": lineno})


class DatabaseDatatypeDependencyStatus(LeafStatus):
    def __init__(self, type_name: str, subject_name: str):
        super().__init__("",
                         "Cannot Modify a Vertex- or EdgeType that is referenced by Another Database Object",
                         False,
                         {"Type Name": type_name, "Name of Object Referenced": subject_name})


class Database:
    """
    A singleton collection of all objects in a SQLonGraphs program. Handles all interaction between the frontend and backend.
    Attributes:
        edgetypes: a dictionary mapping the names of EdgeTypes to the object with this name.
        vertextypes: a dictionary mapping the names of VertexTypes to the object with this name.
        graphs: a dictionary mapping the names of Graphs to the object with this name.
    """

    def __init__(self):
        """
        Constructor for Database, only used once.
        """
        self.edgetypes: dict[str, EdgeType] = {}
        self.vertextypes: dict[str, VertexType] = {}
        self.graphs: dict[str, Graph] = {}

    def names(self) -> list[str]:
        return list(self.edgetypes.keys()) + list(self.vertextypes.keys()) + list(self.edgetypes.keys())

    def create_edgetype(self, name: str, names: list[str], types: dict[str, PrimitiveTypes],
                        constraints: tuple[TypewideConstraint, list[str]], lineno: int) -> Status:
        """
        Create an edge type with the given name, field names, field types and constraints.
        If the name previously existed as a name of any database object, or if calling check_constraints() on the
        created edge type returns an error, then no new types will be created and a Statuses with ERRORs will be thrown.
        Otherwise, the created edge type is addressable by the supplied name in self.edgetypes.
        """
        bounded = [BoundTypewideConstraint(constraint, fields) for constraint, fields in constraints]
        edgetype = EdgeType(name, names, types, bounded)
        name_status = DatabaseNameNoDuplicatesStatus(name in self.names(), name, lineno)
        check_status = edgetype.check_constraints({})
        status = DatabaseOperationStatus("CREATE EDGETYPE", [name_status, check_status], name, lineno)
        if status.success:
            self.edgetypes[name] = edgetype
        return status

    def create_vertextype(self, name: str, names: list[str], types: dict[str, PrimitiveTypes],
                          constraints: dict[TypewideConstraint, list[str]], lineno: int) -> Status:
        """
        Create a vertex type with the given name, field names, field types and constraints.
        If the name previously existed as a name of any database object, or if calling check_constraints() on the
        created edge type returns an error, then no new types will be created and a Statuses with ERRORs will be thrown.
        Otherwise, the edge type is addressable by the supplied name in self.vertextypes
        """
        bounded = [BoundTypewideConstraint(constraint, fields) for constraint, fields in constraints]
        vertextype = VertexType(name, names, types, bounded)
        name_status = DatabaseNameNoDuplicatesStatus(name in self.names(), name, lineno)
        check_status = vertextype.check_constraints({})
        status = DatabaseOperationStatus("CREATE VERTEXTYPE", [name_status, check_status], name, lineno)
        if status.success:
            self.vertextypes[name] = vertextype
        return status

    def create_graph(self, name: str, edgetype_name: str, vertextype_name: str,
                     constraints: list[GraphwideConstraint], lineno: int) -> Status:
        graph_name_status = DatabaseNameNoDuplicatesStatus(name in self.names(), name, lineno)
        edgetype_name_status = DatabaseNameExistsStatus(name in self.names(), name, lineno)
        vertextype_name_status = DatabaseNameExistsStatus(name in self.names(), name, lineno)
        status = DatabaseOperationStatus("CREATE GRAPH",
                                         [graph_name_status, edgetype_name_status, vertextype_name_status], name,
                                         lineno)
        if status.success:
            self.graphs[name] = Graph(name, self.vertextypes[vertextype_name], self.edgetypes[edgetype_name],
                                      constraints)
        return status

    def insert_graph(self, name: str, lineno: int, vertices: Optional[list[dict[str, Primitive]]] = None,
                     edges: Optional[list[dict[str, Primitive]]] = None) -> Status:
        graph_name_status = DatabaseNameNoDuplicatesStatus(name in self.names(), name, lineno)
        if graph_name_status.success:
            insert_status = self.graphs[name].insert(vertices, edges)
            return DatabaseOperationStatus("INSERT INTO", [insert_status], name, lineno)
        else:
            return DatabaseOperationStatus("INSERT INTO", [graph_name_status], name, lineno)

    def drop(self, name: str, lineno: int) -> Status:
        statuses = [DatabaseNameNoDuplicatesStatus(name in self.names(), name, lineno)]
        if self.graphs.get(name) is not None:
            self.graphs.pop(name)
        elif (edgetype := self.edgetypes.get(name)) is not None:
            flag = True
            for graph in self.graphs.values():
                if graph.edges.datatype == edgetype:
                    statuses.append(DatabaseDatatypeDependencyStatus(name, graph.name))
                    flag = False
            if flag:
                self.edgetypes.pop(name)
        elif (vertextype := self.vertextypes.get(name)) is not None:
            flag = True
            for graph in self.graphs.values():
                if graph.vertices.datatype == vertextype:
                    statuses.append(DatabaseDatatypeDependencyStatus(name, graph.name))
                    flag = False
            if flag:
                self.vertextypes.pop(name)
        return DatabaseOperationStatus("DROP", statuses, name, lineno)


DB = Database()
