"""
Pre-defined custom data sanitizers.
"""
from __future__ import annotations

from typing import Any

from bluejayson.sanitizers._core import sanitizer_function


@sanitizer_function
def strict(value: Any, _annotation: type = None) -> Any:
    """
    Does nothing and returns the value as-is.
    Strict means that no type coercion is performed.
    """
    # TODO: implement this (doing only type validation)
    raise NotImplementedError


@sanitizer_function
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
