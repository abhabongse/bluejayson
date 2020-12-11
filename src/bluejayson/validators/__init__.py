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
from typing import Any


class BaseValidationException(Exception):
    msg: str
    value: Any
    validator: BaseValidator

    def __init__(self, msg: str, value, validator: BaseValidator):
        self.msg = msg
        self.value = value
        self.validator = validator


class ValidationFailed(BaseValidationException):
    """
    Raised when a validator determines that a value should fail the validation.
    """
    pass


class ImproperValidator(BaseValidationException):
    """
    Raised when the validation failed due to validator misconfiguration.
    """
    # TODO: remove this exception
    pass


@dataclass
class BaseValidator(metaclass=ABCMeta):
    """
    Base validator class for all kinds of validations.
    """

    @abstractmethod
    def validate_sub(self, value):
        """
        Checks whether the input value should be considered valid data.
        This method should return `True` upon the completed and successful check
        or otherwise raises :exc:`ValidationFailed` if the value has been deemed invalid.

        It may also raise :exc:`ValidatorMisconfigured` if the check fails
        but due to improper configuration on the validator part.

        Other kinds of exceptions raised from this method will be treated as
        a bug in library implementation of validators.

        This method is intended to be a subroutine method
        amd thus should **not** be called directly;
        please use :meth:`validate` method or use :meth:`__call__` instead.
        """
        raise NotImplementedError

    def validate(self, value, *, raises_error: bool = True) -> bool:
        """
        Checks the input value through a subroutine call to :meth:`validate_sub`.
        When `raises_error` flag is **unset** and a validation failure has happened,
        the :exc:`ValidationFailure` will be replaced with `False` being returned.
        """
        try:
            result = self.validate_sub(value)
        except ValidationFailed:
            if raises_error:
                raise
            return False
        except BaseValidationException:
            raise
        except Exception as exc:
            raise RuntimeError("unexpected exception from validate_sub") from exc
        if result is not True:
            raise RuntimeError(f"validate_sub must either return True or raise BaseValidationException "
                               f"(received {result!r})")
        return True

    def __call__(self, value) -> bool:
        """
        Alias for :meth:`validate` method but strictly returns boolean value
        instead of raising :exc:`ValidationFailure` upon failure.
        """
        return self.validate(value, raises_error=False)


@dataclass
class Predicate(BaseValidator):
    """
    Wraps over a custom predicate function.
    """
    #: Custom predicate function
    custom_func: Callable[[Any], bool]

    #: Whether non-boolean value returned from custom predicate
    #: should be treated as :exc:`ValidationFailure`
    #: TODO: incorporate this attribute
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

    def validate_sub(self, value):
        result = self.custom_func(value)
        if not isinstance(result, bool):
            raise ImproperValidator(f"custom predicate must return boolean "
                                    f"(received {result!r})", value, self)
        if not result:
            raise ValidationFailed("custom predicate is not satisfied", value, self)
        return True


@dataclass
class Equal(BaseValidator):
    """
    Checks whether a value is equal to the given `target`.
    """
    #: Target to compare against
    target: Any

    def validate_sub(self, value):
        if value != self.target:
            raise ValidationFailed(f"value not matching target {self.target!r}", value, self)
        return True


@dataclass
class Range(BaseValidator):
    """
    Checks whether a value falls within the given range.
    """
    #: Lower bound of the range to compare (not checked if not provided)
    min: Any = None

    #: Upper bound of the range to compare (not checked if not provided)
    max: Any = None

    #: Whether to include `min` as part of the range itself
    min_inclusive: bool = True

    #: Whether to include `max` as part of the range itself
    max_inclusive: bool = True

    #: Whether :exc:`TypeError` raised during value comparison
    #: should be treated as :exc:`ValidationFailure`
    #: TODO: incorporate this attribute
    absorb_cmp_error: bool = True

    def __post_init__(self):
        if not isinstance(self.min_inclusive, bool):
            raise TypeError(f"min_inclusive flag must be a boolean (received {self.min_inclusive!r})")
        if not isinstance(self.max_inclusive, bool):
            raise TypeError(f"max_inclusive flag must be a boolean (received {self.max_inclusive!r})")

    def validate_sub(self, value):
        try:
            result = self._compare_lower(value) and self._compare_upper(value)
        except Exception as exc:
            raise ImproperValidator("incomparable value with bounds", value, self) from exc
        if not result:
            statement = self._inequality_statement()
            raise ValidationFailed(f"value outside of range [{statement}]", value, self)
        return True

    def _compare_lower(self, value) -> bool:
        if self.min is None:
            return True
        if self.min_inclusive:
            return value >= self.min
        else:
            return value > self.min

    def _compare_upper(self, value) -> bool:
        if self.max is None:
            return True
        if self.max_inclusive:
            return value <= self.max
        else:
            return value < self.max

    def _inequality_statement(self) -> str:
        statement = '?'
        if self.min is not None:
            op = '<=' if self.min_inclusive else '<'
            statement = f'{self.min} {op} {statement}'
        if self.max is not None:
            op = '<=' if self.max_inclusive else '<'
            statement = f'{statement} {op} {self.max}'
        return statement
