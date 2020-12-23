"""
Main data sanitizing class, consisting of three steps:
1. Type coercion (if set)
2. Type validation
3. Additionally annotated validation
"""
from __future__ import annotations

import datetime as dt
from abc import ABCMeta
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Union


@dataclass
class BaseSanitizer(metaclass=ABCMeta):
    """
    Base sanitizer class for three-step data sanitizations.
    """

    def sanitize(self, value: Any, annotation: type) -> Any:
        # TODO: implement this
        pass

    def coerce(self, value: Any) -> Any:
        return value


@dataclass
class BooleanSanitizer(BaseSanitizer):
    """
    Converts a given value into a boolean.
    These values are recognized as True: '1', 'y', 'yes', 'true', 'on';
    whereas these values are recognized as False: '0', 'n', 'no', 'false', 'off'.
    """

    def coerce(self, value: Any) -> bool:
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


DEFAULT_SANITIZERS: dict[type, Union[BaseSanitizer, Callable]] = {
    dt.datetime: dt.datetime.fromisoformat,
    dt.date: dt.date.fromisoformat,
    dt.time: dt.time.fromisoformat,
    bool: BooleanSanitizer(),
    # TODO: add more data coercion functions for parametric types
}
