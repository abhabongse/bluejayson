"""
Main data sanitizing class, consisting of three steps:
1. Type coercion (if set)
2. Type validation
3. Additionally annotated validation
"""
from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from bluejayson.coercions import boolean_flag


@dataclass
class Sanitizer:
    """
    Base sanitizer class for three-step data sanitizations.
    """
    fallback_coercions: dict[type, Callable]

    def sanitize(self, value: Any, annotation: type) -> Any:
        # TODO: implement this
        raise NotImplementedError


DEFAULT_SANITIZER = Sanitizer({
    dt.datetime: dt.datetime.fromisoformat,
    dt.date: dt.date.fromisoformat,
    dt.time: dt.time.fromisoformat,
    bool: boolean_flag,
    # TODO: add more data coercion functions for parametric types
})
