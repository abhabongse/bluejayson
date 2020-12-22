"""
Collection of default coercion functions.
"""
from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from typing import Any

CoerceFunc = Callable[[Any], Any]


def parse_boolean_flag(value: Any) -> bool:
    """
    Converts a given value into a boolean.
    These values are recognized as True: '1', 'y', 'yes', 'true', 'on';
    whereas these values are recognized as False: '0', 'n', 'no', 'false', 'off'.
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


DEFAULT_COERCE_FUNCS: dict[type, CoerceFunc] = {
    dt.datetime: dt.datetime.fromisoformat,
    dt.date: dt.date.fromisoformat,
    bool: parse_boolean_flag,
}