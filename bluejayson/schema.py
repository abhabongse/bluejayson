from collections import OrderedDict
from inspect import Signature, Parameter
from typing import Dict

from bluejayson.fields import BaseField


class SchemaMeta(type):
    """
    Companion class constructor for :py:class:`BaseSchema` and
    all of its derivatives.
    """

    def __new__(mcs, name, bases, dct):
        all_fields = mcs._gather_all_fields(name, bases, dct)
        dct['bjs_all_fields'] = all_fields
        dct['__signature__'] = mcs._create_signature(all_fields)
        return super().__new__(mcs, name, bases, dct)

    @classmethod
    def _gather_all_fields(mcs, name, bases, dct):
        all_fields = OrderedDict()

        # Construct the class just for MRO (will be discarded)
        cls = super().__new__(mcs, name, bases, dct)

        # Gather fields from parent classes in reversed MRO
        for parent_cls in cls.mro()[-1:0:-1]:
            if not hasattr(parent_cls, 'bjs_all_fields'):
                continue
            for name, field in getattr(parent_cls, 'bjs_all_fields').items():
                all_fields[name] = field

        # Additionally gather fields from class dict
        for name, field in cls.__dict__.items():
            if isinstance(field, BaseField):
                all_fields[name] = field

        return all_fields

    @classmethod
    def _create_signature(mcs, all_fields):
        parameters = []

        for name, field in all_fields.items():
            if field.default is BaseField.empty:
                param = Parameter(name, kind=Parameter.KEYWORD_ONLY)
            else:
                param = Parameter(name, kind=Parameter.KEYWORD_ONLY, default=field.default)
            parameters.append(param)

        return Signature(parameters=parameters)


class BaseSchema(metaclass=SchemaMeta):
    """
    Base Schema class for data definitions.
    """
    bjs_all_fields: Dict[str, BaseField]

    def __init__(self, **params):
        cls = type(self)

        # TODO: Resolve parameters and field defaults
        # TODO: Value validations
        for name, value in params.items():
            if name not in cls.bjs_all_fields:
                raise TypeError(f"unknown field {name}")
            setattr(self, name, value)

    def __repr__(self):
        cls = type(self)
        return self.bjs_repr_string(cls.bjs_all_fields)

    def bjs_repr_string(self, field_names):
        """
        Produce string representation of the object using the give list of field names.
        It is intended to be called by :py:meth:`object.__repr__` method.

        Args:
            field_names: List of all fields to show in represented output

        Returns:
            String representation of an instance of the schema.
        """
        clsname = type(self).__qualname__
        params = [
            f"{name}={getattr(self, name)!r}"
            for name in field_names
        ]
        return f"<{clsname}{' ' if params else ''}{' '.join(params)}>"
