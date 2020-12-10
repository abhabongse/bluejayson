from __future__ import annotations

from typing import Optional, Type

from bluejayson.formatters import Formatter
from bluejayson.parsers import Parser
from bluejayson.sanitizers import Sanitizer
from bluejayson.schema import BaseSchema


class _Empty:
    pass


class BaseField:
    """
    Constructs a field in the schema definition with appropriate parsers,
    sanitizers, and formatters.

    Attributes:
        parser: Instance of :py:class:`Parser` class which will help parsing
            JSON strings and JSON-structured objects into intermediate results
            which will then be passed to sanitizers.
        sanitizer: Instance of :py:class:`Sanitizer` class which will help
            validate and sanitize values (which either already have been parsed
            or is provided directory to the constructor).
        formatter: Instance of :py:class:`Formatter` class which does the
            opposite job of parsers: to convert value back into JSON strings
            or JSON-structured objects.
    """
    empty = _Empty

    def __init__(
            self,
            default=_Empty,
            parser: Parser = None,
            sanitizer: Sanitizer = None,
            formatter: Formatter = None,
    ):
        self.default = default
        self.parser = parser or Parser()
        self.sanitizer = sanitizer or Sanitizer()
        self.formatter = formatter or Formatter()

    def __set_name__(self, owner: Type[BaseSchema], name: str):
        self.field_name = name

    def __set__(self, instance: BaseSchema, value):
        value = self.sanitizer(value)
        instance.__dict__[self.field_name] = value

    def __get__(self, instance: Optional[BaseSchema], owner: Type[BaseSchema]):
        if instance is None:
            return self
        if self.field_name not in instance.__dict__ and self.default is not BaseField.empty:
            instance.__dict__[self.field_name] = self.default() if callable(self.default) else self.default
        return instance.__dict__[self.field_name]


class StrField(BaseField):
    pass


class IntField(BaseField):
    pass


class BoolField(BaseField):
    pass


class ListField(BaseField):
    def __init__(self, val_type: Type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.val_type = val_type


class DictField(BaseField):
    def __init__(self, val_type: Type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.val_type = val_type
