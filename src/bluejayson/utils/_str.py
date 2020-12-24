"""
String utility functions.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def prepare_repr(name: str, fields: Mapping[str, Any]) -> str:
    """
    Prepares a comma-separated list of fields as a substring suitable for __repr__.
    """
    fields_str = ', '.join(f'{k}={v!r}' for k, v in fields.items())
    return f"{name}({fields_str})"
