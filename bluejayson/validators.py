from typing import Optional, Callable, Any

from bluejayson.exceptions import ValidationError
from bluejayson.sanitizers import Sanitizer


class Validator(Sanitizer):
    """
    Validation wrapper over a function or a lambda which returns True if and only if
    the value of the input argument passes the validation.
    """

    def __init__(self, validate_func: Callable[[Any], bool], description: Optional[str] = None):
        self.validate_func = validate_func
        self.description = (description or getattr(validate_func, '_description_')
                            or f"validation failed on function {validate_func.__qualname__}")

    def sanitize(self, value):
        validation_result = self.validate_func(value)
        if not validation_result:
            raise ValidationError(self.description)
        return value


###############################
# Validator factory functions #
###############################


def is_exactly(target):
    """
    Constructs a validator to check whether a value exactly matches the target.
    Args:
        target: Expected value

    Returns:
        An instance of :py:class:`Validator`.
    """
    return Validator(lambda value: value == target, f"should exactly match {target!r}")


def upper_bound(limit, inclusive: bool = True) -> Validator:
    """
    Constructs an upper limit validator.

    Args:
        limit: Maximum allowed value
        inclusive: Whether to include the limit as part of allowed value

    Returns:
        An instance of :py:class:`Validator`.
    """
    if inclusive:
        return Validator(lambda value: value <= limit, f"cannot be greater than {limit!r}")
    else:
        return Validator(lambda value: value < limit, f"cannot be {limit!r} or greater")


def lower_bound(limit, inclusive: bool = True) -> Validator:
    """
    Constructs a lower limit validator.

    Args:
        limit: Minimum allowed value
        inclusive: Whether to include the limit as part of allowed value

    Returns:
        An instance of :py:class:`Validator`.
    """
    if inclusive:
        return Validator(lambda value: value >= limit, f"cannot be less than {limit!r}")
    else:
        return Validator(lambda value: value > limit, f"cannot be {limit!r} or less")


def between(lower_limit, upper_limit, inclusive: bool = True,
            lower_inclusive: Optional[bool] = None, upper_inclusive: Optional[bool] = None):
    """
    Constructs a validator for a range of allowed values.

    Args:
        lower_limit: Minimum allowed value
        upper_limit: Maximum allowed value
        inclusive: Whether to include the limits as part of allowed value
        lower_inclusive: Whether to include the lower limit as part of allowed value
            (overrides inclusive)
        upper_inclusive: Whether to include the upper limit as part of allowed value
            (overrides inclusive)

    Returns:
        An instance of :py:class:`Validator`.
    """
    lower_inclusive = inclusive if lower_inclusive is None else lower_inclusive
    upper_inclusive = inclusive if upper_inclusive is None else upper_inclusive
    if lower_inclusive and upper_inclusive:
        return Validator(lambda value: lower_limit <= value <= upper_limit,
                         f"must be between {lower_limit!r} and {upper_limit!r} (inclusive)")
    elif lower_inclusive:
        return Validator(lambda value: lower_limit <= value < upper_limit,
                         f"must be between {lower_limit!r} (inclusive) and "
                         f"{upper_limit!r} (exclusive)")
    elif upper_inclusive:
        return Validator(lambda value: lower_limit < value <= upper_limit,
                         f"must be between {lower_limit!r} (exclusive) and "
                         f"{upper_limit!r} (inclusive)")
    else:
        return Validator(lambda value: lower_limit < value < upper_limit,
                         f"must be between {lower_limit!r} and {upper_limit!r} (exclusive)")
    

def max_length(limit):
    """
    Constructs a validator to check for maximum length of a container.

    Args:
        limit: Maximum length allowed

    Returns:
        An instance of :py:class:`Validator`.
    """
    return Validator(lambda value: len(value) <= limit, f"length cannot be greater than {limit!r}")


def min_length(limit):
    """
    Constructs a validator to check for minimum length of a container.

    Args:
        limit: Minimum length allowed

    Returns:
        An instance of :py:class:`Validator`.
    """
    return Validator(lambda value: len(value) >= limit, f"length cannot be less than {limit!r}")


def length_between(lower_limit, upper_limit):
    """
    Constructs a validator for a range of allowed values.

    Args:
        lower_limit: Minimum length allowed value
        upper_limit: Maximum length allowed value

    Returns:
        An instance of :py:class:`Validator`.
    """
    return Validator(lambda value: lower_limit <= len(value) <= upper_limit,
                     f"length must be between {lower_limit!r} and {upper_limit!r} (inclusive)")
