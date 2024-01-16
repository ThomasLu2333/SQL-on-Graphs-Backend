from typing import Optional, Any


class Status:
    """
    DEPRECATED. Represents the statuses of an operation, which is either success or error.
    Attributes:
        success: represents whether the ooperation had succeeded
        message: an error message if success is false, or a success message otherwise
        context: a dictionary of context information (e.g. line number) of the operation.
    """

    def __init__(self, message : str, success : bool):
        """
        Initializes a Status object with the given attributes and an empty context.
        """
        self.message = message
        self.success = success
        self.context: dict[str, Any] = {}

    def put_context(self, context_name: str, context_value: Any):
        """
        Put a context information to the Status.
        :param context_name: name for the context (e.g. line number)
        :param context_value: value in the context (e.g. 11)
        :return:
        """
        self.context[context_name] = context_value

    def get_context(self, context_name: str):
        """
        Return the context information associated with this context name which must exist.
        """
        return self.context[context_name]

    def __str__(self):
        """
        :return: A string representation of a Status.
        """
        first = f"OK: {self.message}\n" if self.success else f"ERROR: {self.message}\n"
        if len(self.context.values()) != 0:
            items = list(self.context.items())
            second = ("in\n" +
                      "\n".join([f"  {name}: {str(value)}, " for name, value in items[:-1]] +
                                [f"  {items[-1][0]}: {str(items[-1][1])}.\n"])
                      )
            return first + second
        return first

    def __getitem__(self, item: str):
        return self.context[item]

    def __setitem__(self, key : str, value : any):
        self.put_context(key, value)


class Statuses:
    """
    Represents a collection of statuses.
    Attributes:
        statuses: the list of statuses contained in this object.
    """

    def __init__(self, statuses: Optional[list[Status]] = None):
        """
        Creates a Statuses object.
        :param statuses: The initial list of statuses contained in the object. self.
        """
        self.statuses: list[Status] = [] if statuses is None else statuses

    def add_status(self, status: Status):
        """
        Add another statuses object to this Statuses.
        """
        self.statuses.append(status)

    def errors(self):
        return list(filter(lambda x: not x.success, self.statuses))

    def num_errors(self):
        """
        Returns the number of error statuses in the Statuses.
        """
        return len(self.errors())

    def has_errors(self):
        """
        Returns whether the Statuses contain errors.
        """
        return self.num_errors() > 0

    @staticmethod
    def merge(*args):
        """
        Returns a Statuses object that combines the lists of statuses from multiple Statuses object
        """
        new_statuses = []
        for arg in args:
            new_statuses.extend(arg.statuses)
        return Statuses(new_statuses)

    def add_context(self, name: str, value: Any):
        """
        Add a context information to all statuses inside this object.
        """
        for status in self.statuses:
            status.put_context(name, value)

    def __str__(self):
        """
        :return: A string representation of a Statuses.
        """
        statuses = list(reversed(self.statuses))
        first = f"Summary: {len(statuses) - self.num_errors()} OKs, {self.num_errors()} ERRORs.\n"
        second = "".join([f"{i + 1} -- " + str(status) for i, status in enumerate(statuses)])
        return first + second

    def errors_to_string(self):
        """
        :return: A string representation of a Statuses, only including the ERROR Status objects.
        """
        first = "ALL OK" if not self.has_errors() else f"{self.num_errors()} ERRORs Occurred:\n"
        second = "".join([f"{i + 1} -- " + str(status) for i, status in enumerate(reversed(self.errors()))])
        return first + second

    def __iter__(self):
        """
        Return an iterable view of the Statuses inside this object.
        """
        return self.statuses.__iter__()