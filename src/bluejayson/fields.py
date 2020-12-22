"""
Main definition of data field class.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any, Optional, Union, get_args, get_origin, get_type_hints

from bluejayson.coercions import DEFAULT_COERCE_FUNCS
from bluejayson.exceptions import BlueJaysonError
from bluejayson.validators import BaseValidator

CoerceFunc = Callable[[Any], Any]


@dataclass(init=False, repr=False, order=False)
class FieldFactory:
    """
    A factory which helps construct instances of :cls:`Field` class
    with a pre-specified underlying configuration,
    such as a default set of type coercion functions when a field needs it.
    """
    coerce_funcs: dict[type, CoerceFunc]

    def __init__(self, extra_coerce_funcs: dict[type, CoerceFunc] = None):
        self.coerce_funcs = DEFAULT_COERCE_FUNCS | (extra_coerce_funcs or {})

    def field(self, *args, **kwargs) -> Field:
        """
        Constructs a field instance, passing itself as the factory.
        """
        return Field(*args, factory=self, **kwargs)

    def resolve_coerce_func(self, dtype: type, specifier: Union[CoerceFunc, bool]) -> Optional[CoerceFunc]:
        """
        Obtain the resolved type coercion function based on the target `dtype`
        and the coercion `specifier` given to the :cls:`Field` constructor.
        """
        if specifier is True:
            if not isinstance(dtype, type):
                raise TypeError(f"dtype required as type but received {dtype}")
            return self.coerce_funcs.get(dtype, dtype)
        if specifier is False:
            return None
        return specifier


DEFAULT_FIELD_FACTORY = FieldFactory()


@dataclass(init=False, order=False)
class Field:
    """
    Data field class which can be utilized as a standalone instance
    (for a single value data sanitization, etc.)
    or as a data descriptor for an attribute of a subclass of
    :cls:`bluejayson.prodtype.ProductType`.
    """
    attr_name: Optional[str]
    dtype: type
    extra_annotations: tuple
    coerce: Union[bool, CoerceFunc]
    factory: FieldFactory

    def __init__(self, dtype: type = None,
                 *extra_annotations,
                 coerce: Union[bool, CoerceFunc] = True,
                 factory: FieldFactory = DEFAULT_FIELD_FACTORY):
        self.attr_name = None
        self.dtype = dtype
        self.extra_annotations = extra_annotations
        self.coerce = coerce
        self.factory = factory

    def __set_name__(self, owner, name):
        self.attr_name = name
        try:
            self.dtype = self.dtype or get_type_hints(owner)[name]
        except KeyError:
            pass
        try:
            full_annotations = get_type_hints(owner, include_extras=True)[name]
        except KeyError:
            pass
        else:
            if get_origin(full_annotations) is Annotated:
                self.extra_annotations += get_args(full_annotations)[1:]

    def sanitize(self, value: Any) -> Any:
        """
        Ensure that a given input value is of the pre-specified :attr:`dtype`,
        and that it passes all the validators provided as :attr:`extra_annotations`.
        If :attr:`coerce` function is set, it will be used to transform
        the given input value into the destination type before any validations.
        """
        value = self._coerce_value(value)
        self._validate_value(value)
        return value

    def _coerce_value(self, value: Any) -> Any:
        coerce_func = self.factory.resolve_coerce_func(self.dtype, self.coerce)
        if coerce_func:
            original_value = value
            value = coerce_func(value)
            if not isinstance(value, self.dtype):
                raise BlueJaysonError(f"failed to coerce input value to type {self.dtype.__qualname__} "
                                      f"(received {original_value!r})")
        elif not isinstance(value, self.dtype):
            raise BlueJaysonError(f"input value mismatched from type {self.dtype.__qualname__} "
                                  f"(but received {value!r})")
        return value

    def _validate_value(self, value: Any) -> Any:
        for validator in self.extra_annotations:
            if isinstance(validator, BaseValidator):
                validator.validate(value)
        return value
