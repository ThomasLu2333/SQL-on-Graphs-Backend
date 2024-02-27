from typing import Optional, Union

from constraints.typewide import TypewideConstraint
from datatypes.primitive import PrimitiveTypes, Primitive, NULL
from datatypes.vertex import VertexType
from statuses.status import *
from datatypes.raw import RawType, ID
from utilities.Transaction import Transaction


class DataAddEntriesStatus(DerivedStatus):
    def __init__(self, datatype: RawType, substatuses):
        item = 'Vertices' if isinstance(datatype, VertexType) else 'Edges'
        super().__init__(f"Adding {item} Successful -- All Changes Saved",
                         f"Adding {item} Failed -- Changed Rolled Back",
                         substatuses)

class DataGetFieldStatus(LeafStatus):
    def __init__(self, field_name : str, data: Optional[list[Primitive]] = None):
        context = {"Field Name":field_name}
        if data is not None:
            context["data"] = data
        super().__init__("Field successfully fetched",
                         "Field does not exist",
                         True if data is not None else False,
                         context)


class Data:
    """
    A container for a list of entries. Each entry containing a value each from a list of fields which have a name,
    a type, and constraints and are defined by either an EdgeType or VertexType. Data provides three views to
    access the entries under different circumstances.
    Attributes:
        datatype: the type of the edges or vertices.
        values: a dictionary mapping each field name to a list of values that the field has.
                Each list of values must have the same length.
        ids: a list of values of the id field.
        entries: a dictionary mapping each id to the entry with this id.
        last: a Transaction object showing last operation done onto this object. None if newly created.
    """

    class INSERTDataTransaction(Transaction):
        """
        Represents an INSERT transaction done to a matrix.
        """
        pass

    def __init__(self, datatype: RawType):
        """
        Initialize an empty Data container with the given type, which must be valid as indicated by
            RawType.check_constraints().
        """
        self.datatype = datatype
        self.values: dict[str, list[Primitive]] = dict(zip(datatype.names,
                                                           [[] for _ in range(len(datatype.names))]
                                                           ))
        self.ids: list[Primitive] = []
        self.entries: dict[Primitive, dict[str, Primitive]] = {}

    def add_entry(self, entry: dict[str, Primitive]) -> Status:
        """
        Adds an entry to the container. If self.datatype_check_constraints() after the addition returns a Statuses with ERRORs,
            then the addition will be rolled back and a Statuses containing ERRORs will be thrown. Otherwise,
            the addition is saved and OK Statuses will be returned.
        :param entry: a dictionary mapping each field to a value that will be added to the field.
        :returns: a Statuses object showing result of this operation.
        """
        return self.add_entries([entry])

    def add_entries(self, entries: list[dict[str, Primitive]]) -> Status:
        """
        Adds multiple entries to the container.
        :param entries: a list of entries.
        :return: a Statuses object showing result of this operation. This operation is NOT ROLLED BACK even if it's
            unsuccessful.
        """
        deltas: dict[str, list[Primitive]] = {key: [] for key in self.datatype.names}
        for entry in entries:
            for key in self.datatype.names:
                value = entry.get(key, NULL)
                deltas[key].append(value)
                self.values[key].append(value)
        status = self.datatype.check_constraints(self.values, deltas)
        new_status = DataAddEntriesStatus(self.datatype, [status])
        for entry in entries:
            self.ids.append(entry[ID])
            self.entries[entry[ID]] = entry
        return new_status

    def rollback(self, entries: list[dict[str, Primitive]]):
        #TODO: implement completely the Rollback class to handle all insertions, deletions, and updates
        for _ in range(len(entries)):
            for key in self.datatype.names:
                self.values[key].pop()
        for _ in range(len(entries)):
            id = self.ids.pop()
            self.entries.pop(id)

    def size(self) -> int:
        """
        Return the length of each of the values in the values field.
        """
        return len(self.entries)

    def get_field(self, field_name: str) -> Status:
        """
        Return an OK Status object containing the list of primitive type values for the field with name 'field_name'
        in the context named "data".
        """
        return DataGetFieldStatus(field_name, self.values.get(field_name))

    def get_entry(self, id: Primitive) -> Optional[dict[str, Primitive]]:
        """
        Return the entry with id 'id'. If such id doesn't exist, then None is returned.
        """
        return self.entries.get(id)

    def get_entries(self) -> list[dict[str, Primitive]]:
        """
        Return a list of all entries in self.entries.
        """
        return list(self.entries.values())
