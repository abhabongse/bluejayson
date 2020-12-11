"""
Collection of data validators.

Many of these validators are heavily inspired by those from marshmallow.
https://marshmallow.readthedocs.io/en/stable/marshmallow.validate.html
"""
from __future__ import annotations

import inspect
from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal


class ValidationFailed(Exception):
    """
    This exception is raised when a validator determines that
    a given value should be considered invalid data.
    """
    msg: str
    value: Any
    validator: BaseValidator

    def __init__(self, msg: str, value, validator: BaseValidator):
        self.msg = msg
        self.value = value
        self.validator = validator


@dataclass
class BaseValidator(metaclass=ABCMeta):
    """
    Base validator class for all kinds of validations.
    """

    @abstractmethod
    def validate_sub(self, value) -> Literal[True]:
        """
        Checks whether an input value should be considered valid data.
        This method should return `True` upon the completed and successful check
        or otherwise raises :exc:`ValidationFailed` if the value considered invalid.

        Other kinds of exceptions raised from this method
        should be treated as one of the following:
        - a validator implementation bug (library's fault)
        - a bug due to improper validator setup (caller's fault)

        This method is intended to be called as a subroutine by :meth:`validate` method
        (or as a callable) and thus should **not** be called directly.
        """
        raise NotImplementedError

    def validate(self, value) -> bool:
        """
        Checks whether an input value through a subroutine call to :meth:`validate_sub`.
        """
        try:
            result = self.validate_sub(value)
        except ValidationFailed:
            raise
        if result is not True:
            raise RuntimeError(f"validate_sub should have returned either True "
                               f"or raise ValidationFailure (but received {result!r})")
        return True

    def __call__(self, value) -> bool:
        """
        Alias method for :meth:`validate` method but converts :exc:`ValidationFailure`
        into returning `False` instead.
        """
        try:
            return self.validate(value)
        except ValidationFailed:
            return False


@dataclass
class Predicate(BaseValidator):
    """
    Wraps over a custom predicate (boolean) function.
    """
    #: Custom predicate function
    custom_func: Callable[[Any], bool]

    #: Indicates whether non-boolean value returned from custom predicate
    #: should be treated as :exc:`TypeError` instead
    strict: bool = True

    def __post_init__(self):
        self._check_custom_predicate(self.custom_func)

    @classmethod
    def _check_custom_predicate(cls, validate_func):
        sig = inspect.signature(validate_func)
        if not sig.parameters:
            raise TypeError("custom predicate must accept at least one argument")
        first, *rest = sig.parameters.keys()

        if sig.parameters[first].kind not in [
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.VAR_POSITIONAL,
        ]:
            raise TypeError("first argument of the custom predicate must be accepted positionally")

        if not all(sig.parameters[name].default != inspect.Parameter.empty for name in rest):
            raise TypeError("other arguments after first of the custom predicate must be optional")

    def validate_sub(self, value) -> Literal[True]:
        result = self.custom_func(value)
        if self.strict and not isinstance(result, bool):
            raise TypeError(f"custom predicate must return boolean in strict mode (but received {result!r})")
        if not result:
            raise ValidationFailed("custom predicate is not satisfied", value, self)
        return True


@dataclass
class Equal(BaseValidator):
    """
    Checks whether a given value matches (i.e. is equal to) the given `target`.
    """
    #: Target to compare the value against
    target: Any

    def validate_sub(self, value) -> Literal[True]:
        if value != self.target:
            raise ValidationFailed(f"value not matching target {self.target!r}", value, self)
        return True


@dataclass
class Range(BaseValidator):
    """
    Checks whether a given value falls within a defined bounded range.
    """
    #: Lower bound of the range to compare the value against (not checked if not provided)
    min: Any = None

    #: Upper bound of the range to compare the value against (not checked if not provided)
    max: Any = None

    #: Indicating whether to include `min` as part of the range itself
    min_inclusive: bool = True

    #: Indicating whether to include `max` as part of the range itself
    max_inclusive: bool = True

    #: Whether :exc:`TypeError` raised due to value comparison operation
    #: should be treated as :exc:`ValidationFailure` instead
    absorb_cmp_error: bool = True

    def __post_init__(self):
        if not isinstance(self.min_inclusive, bool):
            raise TypeError(f"min_inclusive flag must be a boolean (but received {self.min_inclusive!r})")
        if not isinstance(self.max_inclusive, bool):
            raise TypeError(f"max_inclusive flag must be a boolean (but received {self.max_inclusive!r})")

    def validate_sub(self, value) -> Literal[True]:
        try:
            result = self._compare_lower(value) and self._compare_upper(value)
        except TypeError as exc:
            if self.absorb_cmp_error:
                statement = self._inequality_statement()
                raise ValidationFailed(f"cannot compare value against the range [{statement}]", value, self) from exc
            raise
        if not result:
            statement = self._inequality_statement()
            raise ValidationFailed(f"value outside of range [{statement}]", value, self)
        return True

    def _compare_lower(self, value) -> bool:
        return self.min is None or (value >= self.min if self.min_inclusive else value > self.min)

    def _compare_upper(self, value) -> bool:
        return self.max is None or (value <= self.max if self.max_inclusive else value < self.max)

    def _inequality_statement(self) -> str:
        statement = '?'
        if self.min is not None:
            op = '<=' if self.min_inclusive else '<'
            statement = f'{self.min} {op} {statement}'
        if self.max is not None:
            op = '<=' if self.max_inclusive else '<'
            statement = f'{statement} {op} {self.max}'
        return statement


@dataclass
class Length(BaseValidator):
    """
    Checks whether a given value has the length adhering to the specified bounded range.
    """
    #: Lower bound of the range to compare the value against (not checked if not provided)
    min: int = None

    #: Upper bound of the range to compare the value against (not checked if not provided)
    max: int = None

    #: The exact expected length of the value
    #: (ignoring `min` and `max` if this value is specified)
    equal: int = None

    #: Whether :exc:`TypeError` raised due to computation of length (via `len` function)
    #: should be treated as :exc:`ValidationFailure` instead
    absorb_len_error: bool = True

    def __post_init__(self):
        if self.equal is None:
            if self.min is not None and not isinstance(self.min, int):
                raise TypeError(f"min should be int if provided (but received {self.min!r})")
            if self.max is not None and not isinstance(self.max, int):
                raise TypeError(f"max should be int if provided (but received {self.max!r})")
        elif not isinstance(self.equal, int):
            raise TypeError(f"equal should be int if provided (but received {self.equal!r})")

    def validate_sub(self, value) -> Literal[True]:
        try:
            length = len(value)
        except TypeError as exc:
            if self.absorb_len_error:
                raise ValidationFailed("cannot compute length of value", value, self) from exc
            raise
        result = self._compare_lower(length) and self._compare_upper(length)
        if not result:
            statement = self._inequality_statement()
            raise ValidationFailed(f"length outside of range [{statement}]", value, self)
        return True

    def _compare_lower(self, length: int) -> bool:
        return self.min is None or self.min <= length

    def _compare_upper(self, length: int) -> bool:
        return self.max is None or length <= self.max

    def _inequality_statement(self) -> str:
        statement = '?'
        if self.min is not None:
            statement = f'{self.min} <= {statement}'
        if self.max is not None:
            statement = f'{statement} <= {self.max}'
        return statement
