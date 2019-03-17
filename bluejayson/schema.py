from collections import OrderedDict
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

    def __call__(cls: 'BaseSchema', **params):
        instance = super().__call__()

        # Assign all provided parameters
        for name, value in params.items():
            if name not in cls.bjs_all_fields:
                raise TypeError(f"unknown field {name}")
            setattr(instance, name, value)

        # TODO: Verify all parameters

        return instance


class BaseSchema(metaclass=SchemaMeta):
    """
    Base Schema class for data definitions.
    """
    bjs_all_fields: Dict[str, BaseField]

    def __repr__(self):
        cls = type(self)
        return self.bjs_repr_string(cls.bjs_all_fields)

    def bjs_repr_string(self, field_names):
        clsname = type(self).__qualname__
        params = [
            f"{name}={getattr(self, name)!r}"
            for name in field_names
        ]
        return f"<{clsname}{' ' if params else ''}{' '.join(params)}>"
