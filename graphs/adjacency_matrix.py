from datatypes.primitive import Primitive
from graphs.data import Data
from utilities.Transaction import Transaction


class Matrix:
    """
    TODO: Complete this class
    An adjacency matrix supporting rollback.
    Attributes:
        vertices: a Data object containing the vertices of a graph.
        edges: a Data object containing the edges of a graph.
        M: The underlying matrix. Maps the id of a vertex to a list of edges coming out of it.
        last: a Transaction object showing last operation done onto this object. None if newly created.
    """

    class INSERTMatrixTransaction(Transaction):
        """
        Represents an INSERT transaction done to a matrix.
        """
        pass

    def __init__(self, vertices : Data, edges: Data):
        """
        Creates a Matrix from the given vertices and edges.
        """
        pass

    def get_edges(self, vid : Primitive) -> list[dict[str, Primitive]]:
        """
        Returns a list of edges coming out of the vertex with id vid.
        """
        pass

    def get_neighbors(self, vid : Primitive) -> list[dict[str, Primitive]]:
        """
        Returns a list of vertices neighboring this vertex with id vid.
        """
        pass

    def connects(self, vid1 : Primitive, vid2: Primitive) -> bool:
        """
        Returns whether the vertices with id vid1 and vid2 are connected.
        """

    def add_entries(self, entries: list[dict[str, Primitive]]):
        """
        Adds a list of entries to the given adjacency matrix
        """
        pass

    def rollback(self):
        """
        Rollback the last operation done to this matrix.
        The matrix will return to the state before the last operation is executed.
        """
        pass


