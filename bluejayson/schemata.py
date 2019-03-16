from typing import TYPE_CHECKING, List

# TODO: Introduce metaclass for BaseSchema


class BaseSchema:
    """
    Base Schema class for data definitions.

    Attributes:
        schema_all_fields: List of all associated fields in order. It is populated using
            :py:meth:`object.__set_name__` method of the field data descriptor and
            :py:meth:`object.__init_subclass__` class method upon extending classes.
    """
    schema_all_fields: List[str] = []

    # TODO: Introduce __init__ function

    @classmethod
    def _add_field(cls, field_name):
        # Ensure the schema_all_fields is a copy from the parent class
        if 'schema_all_fields' not in cls.__dict__:
            cls.schema_all_fields: List[str] = list(cls.schema_all_fields)
        cls.schema_all_fields.append(field_name)

    def __repr__(self):
        clsname = type(self).__qualname__
        params = []  # TODO: fill this in
        return f"<{clsname}{' ' if params else ''}{' '.join(params)}>"

