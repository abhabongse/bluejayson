"""
Main data sanitization and accompanied utility classes.
"""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable

CoerceFunc = Callable[[Any, type], Any]


@dataclass
class BaseSanitizer(metaclass=ABCMeta):
    """
    Base type coercion class.
    """

    @abstractmethod
    def coerce(self, value: Any, annotation: type = None) -> Any:
        raise NotImplementedError

    def __call__(self, value: Any, annotation: type = None) -> Any:
        return self.coerce(value, annotation)


@dataclass
class sanitizer_function(BaseSanitizer):
    """
    Coercion function decorator.
    The decorated function must accept two arguments:
    1. the value to be coerced
    2. the type annotation for such coercion
    """
    wrapped: CoerceFunc

    def coerce(self, value: Any, annotation: type = None) -> Any:
        return self.wrapped(value, annotation)


@dataclass
class SanitizeRunner:
    """
    Base sanitizer class for three-step data sanitizations.
    """
    fallback_coercions: dict[type, Callable]

    def sanitize(self, value: Any, annotation: type) -> Any:
        # TODO: implement this
        raise NotImplementedError
