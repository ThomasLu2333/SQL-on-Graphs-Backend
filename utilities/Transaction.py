from enum import Enum

from datatypes.primitive import Primitive


class Transaction:
    """
    Represents a Transaction done to a mutable database object.
    Attributes:
        type: the type of transaction.
        data: a list of entries involved in this transaction.
        context: a list of dictionaries representing context information associated with each entry.
    """

    class TransactionType(Enum):
        """
        An Enum member showing the supported transaction types in the current build.
        """
        INSERT = "INSERT"

    def __init__(self, type: TransactionType, data: list[dict[str, Primitive]], context: list[dict]):
        self.type = type
        self.data = data
        self.context = context


