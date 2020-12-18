"""
Collection of data validators.

Many of these validators are heavily inspired by those from marshmallow.
https://marshmallow.readthedocs.io/en/stable/marshmallow.validate.html
"""
from __future__ import annotations

import inspect
import operator
import re
import warnings
from abc import ABCMeta, abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Union

from typing_extensions import Literal

__all__ = [
    'ValidationFailed',
    'BaseValidator',
    'Predicate',
    'Equal',
    'Range',
    'Length',
    'Regexp',
    'InChoices',
]


class ValidationFailed(Exception):
    """
    This exception is raised when a validator determines that
    a given value should be considered invalid data.
    """
    value: Any
    validator: BaseValidator
    error_code: str

    def __init__(self, value: Any, validator: BaseValidator, error_code: str):
        self.value = value
        self.validator = validator
        self.error_code = error_code

    def __str__(self):
        if self.error_code not in self.validator.error_templates:
            warnings.warn(f"unknown error code: {self.error_code!r} "
                          f"of {self.validator.__class__.__qualname__}")
        return (self.validator.error_templates
                .get(self.error_code, "validation failed")
                .format(value=self.value, self=self.validator))


class BaseValidator(metaclass=ABCMeta):
    """
    Base validator class for all kinds of validations.
    """
    # TODO: implements boolean-like operators (NOT, AND, OR, XOR)
    #       to combine multiple sub-validators

    #: Maintains a mapping from error codes (specific to each validator)
    #: to error message templates as {}-formatted strings
    error_templates: ClassVar[dict[str, str]] = {}

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


@dataclass(order=False)
class Predicate(BaseValidator):
    """
    Wraps over a custom predicate (boolean) function.
    """
    error_templates = {
        'not_satisfied': "custom validation function is not satisfied",
    }

    #: Custom predicate function
    pred: Callable[[Any], bool]

    #: Indicates whether non-boolean value returned from the predicate function
    #: should be treated as :exc:`TypeError` instead
    strict: bool = True

    def __post_init__(self):
        self._check_validate_func(self.pred)

    @classmethod
    def _check_validate_func(cls, func):
        sig = inspect.signature(func)
        if not sig.parameters:
            raise TypeError("custom predicate must accept at least one argument")
        first_param, *rest_params = sig.parameters.values()

        if first_param.kind not in [
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.VAR_POSITIONAL,
        ]:
            raise TypeError("first argument of the custom predicate must be accepted positionally")

        for param in rest_params:
            if (param.kind not in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]
                    and param.default == inspect.Parameter.empty):
                raise TypeError("other arguments after first of the custom predicate must be optional")

    def validate_sub(self, value) -> Literal[True]:
        result = self.pred(value)
        if self.strict and not isinstance(result, bool):
            raise TypeError(f"predicate must return boolean in strict mode (but received {result!r})")
        if not result:
            raise ValidationFailed(value, self, 'not_satisfied')
        return True


@dataclass(order=False)
class Equal(BaseValidator):
    """
    Checks whether a given value matches (i.e. is equal to) the given `target`.
    """
    error_templates = {
        'not_matched': 'value not matching target {self.target!r}',
    }

    #: Target to compare the value against
    target: Any

    def validate_sub(self, value) -> Literal[True]:
        if value != self.target:
            raise ValidationFailed(value, self, 'not_matched')
        return True


@dataclass(order=False)
class Range(BaseValidator):
    """
    Checks whether a given value falls within a defined bounded range.
    """
    error_templates = {
        'incomparable': "cannot compare value against the range [{self.range_string}]",
        'out_of_range': "value outside of range [{self.range_string}]",
    }

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
                raise ValidationFailed(value, self, 'incomparable') from exc
            raise
        if not result:
            raise ValidationFailed(value, self, 'out_of_range')
        return True

    def _compare_lower(self, value) -> bool:
        return self.min is None or (value >= self.min if self.min_inclusive else value > self.min)

    def _compare_upper(self, value) -> bool:
        return self.max is None or (value <= self.max if self.max_inclusive else value < self.max)

    @property
    def range_string(self) -> str:
        statement = '?'
        if self.min is not None:
            op = '<=' if self.min_inclusive else '<'
            statement = f'{self.min} {op} {statement}'
        if self.max is not None:
            op = '<=' if self.max_inclusive else '<'
            statement = f'{statement} {op} {self.max}'
        return statement


@dataclass(order=False)
class Length(BaseValidator):
    """
    Checks whether a given value has the length adhering to the specified bounded range.
    """
    error_templates = {
        'uncomputable_length': "cannot compute length of value",
        'length_out_of_range': "length outside of range [{self.range_string}]",
    }

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
                raise ValidationFailed(value, self, 'uncomputable_length') from exc
            raise
        result = self._compare_lower(length) and self._compare_upper(length)
        if not result:
            raise ValidationFailed(value, self, 'length_out_of_range')
        return True

    def _compare_lower(self, length: int) -> bool:
        return self.min is None or self.min <= length

    def _compare_upper(self, length: int) -> bool:
        return self.max is None or length <= self.max

    @property
    def range_string(self) -> str:
        statement = '?'
        if self.min is not None:
            statement = f'{self.min} <= {statement}'
        if self.max is not None:
            statement = f'{statement} <= {self.max}'
        return statement


@dataclass(init=False, order=False)
class Regexp(BaseValidator):
    """
    Checks whether a given string value fully matches the given regular expression.
    """
    error_templates = {
        'not_string': "value must be a string",
        'not_matched': "value does not match the regexp pattern: {self.pattern.pattern}",
        'not_satisfied': "custom validation function is not satisfied",
    }

    #: Input regular expression pattern
    pattern: Union[str, re.Pattern[str]]

    #: Post validate function based on match object
    post_validate: Callable[[re.Match], bool]

    # TODO: implements various calling mode of validation function
    #       (e.g. specifying positional/keyword arguments to function instead of matchobj)
    # TODO: implements validation with recursive Product type
    #       (requires Product type to be implemented first)

    #: Indicates whether non-boolean value returned from the post validation function
    #: should be treated as :exc:`TypeError` instead
    strict: bool

    def __init__(self, pattern: Union[str, re.Pattern[str]],
                 validate_func: Callable[[re.Match], bool] = None,
                 strict: bool = True):
        self.pattern = self._compile_pattern(pattern)
        self.post_validate = validate_func
        self.strict = strict

    @classmethod
    def _compile_pattern(cls, pattern: Union[str, re.Pattern[str]]):
        if isinstance(pattern, re.Pattern):
            return pattern
        if isinstance(pattern, str):
            return re.compile(pattern)
        raise TypeError(f"regexp pattern should be a string or a compiled pattern (but received {pattern!r}")

    def validate_sub(self, value) -> Literal[True]:
        if not isinstance(value, str):
            raise ValidationFailed(value, self, 'not_string')
        matchobj = self.pattern.fullmatch(value)
        if matchobj is None:
            raise ValidationFailed(value, self, 'not_matched')
        if self.post_validate:
            result = self.post_validate(matchobj)
            if self.strict and not isinstance(result, bool):
                raise TypeError(f"post validation function must return boolean in strict mode "
                                f"(but received {result!r})")
            if not result:
                raise ValidationFailed(value, self, 'not_satisfied')
        return True


@dataclass(init=False, order=False)
class InChoices(BaseValidator):
    """
    Checks whether a given value is one among the pre-defined choices.
    """
    error_templates = {
        'not_found': "value not found in choices",
    }

    #: List of choices
    choices: list[Any]

    #: Compare operation
    compare: Callable[[Any, Any], bool]

    #: Indicates whether non-boolean value returned from the post validation function
    #: should be treated as :exc:`TypeError` instead
    strict: bool

    def __init__(self, choices: Sequence[Any],
                 compare: Callable[[Any, Any], bool] = operator.eq,
                 strict: bool = True):
        self.choices = list(choices)
        self.compare = compare
        self.strict = strict

    def validate_sub(self, value) -> Literal[True]:
        for choice in self.choices:
            result = self.compare(value, choice)
            if self.strict and not isinstance(result, bool):
                raise TypeError(f"compare function must return boolean in strict mode "
                                f"(but received {result!r})")
            if result:
                return True
        raise ValidationFailed(value, self, 'not_found')

# TODO: implements Sequence validator which wraps over sub-validator for homogeneous sequence
# TODO: implements Mapping validator with recursive Product type
#       (requires Product type to be implemented first)
