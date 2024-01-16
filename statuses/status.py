from abc import ABCMeta, abstractmethod
from typing import Any


class Status(metaclass=ABCMeta):
    """
    The abstract base class for all Status classes. A Status represents the status of an operation or action
        in a SQLonGraphs program.
    Attributes:
        message: a description of operation being performed
        success: whether the operation succeeded or failed
        context: a dictionary storing key-value pairs of information to accompany message in the self.__str__() method
    """

    @abstractmethod
    def __init__(self, message: str, success: bool, context: dict[str, Any] = None):
        """
        Constructs a BaseStatus with the given message, success, and context (if context is None, then an empty
        context will be initialized)
        """
        self.message = message
        self.success = success
        self.context = context if context is not None else context

    def put_context(self, name: str, value: Any):
        """
        Add a new or change context information to self.context
        """
        self.context[name] = value

    def get_context(self, name: str) -> Any:
        """
        Get the context with name 'name' which must exist.
        """
        return self.context[name]

    def __getitem__(self, item):
        return self.get_context(item)

    def __setitem__(self, key, value):
        return self.put_context(key, value)

    def error_str(self, depth: int = 0):
        """
        The helper method for self.__str__(). Returns the string representation of this Status, showing only errors.
        """
        first = "\t" * depth + (f"OK: {self.message}\n" if self.success else f"ERROR: {self.message}\n")
        second = "\t" * depth + f"  where {str(self.context)[1:-1]}\n"
        return first + second

    def __str__(self):
        return self.error_str()


class LeafStatus(Status):
    """
    The leaf elements in a status hierarchy. The success of a LeafStatus does not depend on any other Statuses.
    """

    def __init__(self, success_message: str, failed_message: str, success: bool, context: dict[str, Any] = None):
        """
        Constructs a LeafStatus with the given message, success, and context (if context is None, then an empty
        context will be initialized)
        """
        super().__init__(success_message if success else failed_message, success, context)


class DerivedStatus(Status):
    """
    The non-leaf elements in a status hiearchy. A DerivedStatus is successful if and only if its list of substatuses
    are all successful.
    Attributes:
        substatuses: a non-empty list of LeafStatuses or DerivedStatuses subsidiary to this DerivedStatus.
    """

    def __init__(self, success_message: str, failed_message: str, substatuses: list[Status],
                 context: dict[str, Any] = None):
        """
        Constructs a DerivedStatus with the given substatuses and context. The message of this DerivedStatus will be
        initialized with success_message and success with True if all statuses in substatuses are successful, and
        failed_message and False otherwise.
        """
        self.substatuses = substatuses
        success = True
        for status in self.substatuses:
            success = success and status.success
        super().__init__(success_message if success else failed_message, success, context)

    def error_str(self, depth: int = 0):
        first = super().error_str(depth)
        if not self.success:
            second = "\t" * depth + "  Causes:\n"
            for status in self.substatuses:
                if not status.success:
                    second += status.error_str(depth + 1)
            return first + second
        return first

    def __str__(self):
        return self.error_str()


class Statuses:
    """
    A collection of BaseStatuses supporting several convenient operations.
    Attributes:
        statuses: a list of statuses.
    """

    def __init__(self, statuses: list[Status] = None):
        self.statuses = statuses if statuses is not None else []

    def add_status(self, status: Status):
        self.statuses.append(status)

    def put_context(self, name: str, value: Any):
        for status in self.statuses:
            status.put_context(name, value)

    def merge(self, other):
        self.statuses = self.statuses + other.statuses
