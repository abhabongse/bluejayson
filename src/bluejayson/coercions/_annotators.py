"""
Annotation-based type coercion functions.
"""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

CoerceFunc = Callable[[Any, type], Any]


@dataclass
class BaseCoercion(metaclass=ABCMeta):
    """
    Base type coercion class.
    """

    @abstractmethod
    def coerce(self, value: Any, annotation: type = None) -> Any:
        raise NotImplementedError

    def __call__(self, value: Any, annotation: type = None) -> Any:
        return self.coerce(value, annotation)


@dataclass
class coerce_function(BaseCoercion):
    """
    Coercion function decorator.
    The decorated function must accept two arguments:
    1. the value to be coerced
    2. the type annotation for such coercion
    """
    wrapped: CoerceFunc

    def coerce(self, value: Any, annotation: type = None) -> Any:
        return self.wrapped(value, annotation)


@coerce_function
def strict(value: Any, _annotation: type = None) -> Any:
    """
    Does nothing and returns the value as-is.
    Strict means that no type coercion is performed.
    """
    return value


@coerce_function
def boolean_flag(value: Any, _annotation: type = None) -> bool:
    """
    Coerces boolean flag string into boolean value.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.strip().lower()
        if value in ['1', 'y', 'yes', 'true', 'on']:
            return True
        if value in ['0', 'n', 'no', 'false', 'off']:
            return False
        raise ValueError(f"cannot convert given value flag to boolean: {value!r}")
    raise TypeError(f"cannot convert given value flag to boolean: {value!r}")
