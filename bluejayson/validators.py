import math
from typing import Optional, Callable, Any

from bluejayson.exceptions import ValidationError
from bluejayson.sanitizers import Sanitizer


class Validator(Sanitizer):
    """
    Validator is a special sanitizer which only validates the value but does
    not transform it.
    """

    def sanitize(self, value):
        self.validate(value)
        return value

    def validate(self, value):
        """
        Perform validation on the given value. This function raises ValidationError
        when the value failed the validation. Otherwise, this function will return
        normally.

        Args:
            value: Value to validate

        Raises:
            ValidationError: Raises when validation failed
        """
        pass


class ValidatorFunc(Validator):
    """
    Validation wrapper over a function or a lambda which returns True if and only if
    the value of the input argument passes the validation.
    """

    def __init__(self, validate_func: Callable[[Any], bool], description: Optional[str] = None):
        self.validate_func = validate_func
        self.description = (description or getattr(validate_func, '__description__')
                            or f"validation failed on function {validate_func.__qualname__}")

    def validate(self, value):
        validation_result = self.validate_func(value)
        if not validation_result:
            raise ValidationError(self.description)


class MaxValue(Validator):

    def __init__(self, limit=math.inf, inclusive: bool = True):
        self.limit = limit
        self.inclusive = inclusive

    def validate(self, value):
        if self.inclusive:
            if value > self.limit:
                raise ValidationError(f"value cannot be greater than {self.limit!r}")
        else:
            if value >= self.limit:
                raise ValidationError(f"value cannot be {self.limit!r} or greater")


class MinValue(Validator):

    def __init__(self, limit=-math.inf, inclusive: bool = True):
        self.limit = limit
        self.inclusive = inclusive

    def validate(self, value):
        if self.inclusive:
            if value < self.limit:
                raise ValidationError(f"value cannot be less than {self.limit!r}")
        else:
            if value <= self.limit:
                raise ValidationError(f"value cannot be {self.limit!r} or less")


class MaxLength(Validator):

    def __init__(self, limit: int = math.inf, inclusive: bool = True):
        self.limit = limit
        self.inclusive = inclusive

    def validate(self, value):
        if self.inclusive:
            if len(value) > self.limit:
                raise ValidationError(f"length cannot be greater than {self.limit!r}")
        else:
            if len(value) >= self.limit:
                raise ValidationError(f"length cannot be {self.limit!r} or greater")


class MinLength(Validator):

    def __init__(self, limit: int = 0, inclusive: bool = True):
        self.limit = limit
        self.inclusive = inclusive

    def validate(self, value):
        if self.inclusive:
            if len(value) < self.limit:
                raise ValidationError(f"length cannot be less than {self.limit!r}")
        else:
            if len(value) <= self.limit:
                raise ValidationError(f"length cannot be {self.limit!r} or less")
