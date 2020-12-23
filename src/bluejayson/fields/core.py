"""
Data field class which defines the type and other validations
for a particular value field.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Union

from typing_extensions import get_type_hints

from bluejayson.fields import FieldFactory

DEFAULT_FIELD_FACTORY = FieldFactory()


@dataclass(order=False)
class Field:
    """
    Data field class which can be utilized either as a standalone instance
    or as a data descriptor for a subclass of :cls:`bluejayson.prodtype.ProductType`.
    """
    attr_name: str = field(init=False, default=None)
    annotation: type = None
    coerce: Union[bool, Callable] = True
    factory: FieldFactory = DEFAULT_FIELD_FACTORY

    def __set_name__(self, owner, name):
        self.attr_name = name
        try:
            self.annotation = self.annotation or get_type_hints(owner, include_extras=True)[name]
        except KeyError:
            pass
