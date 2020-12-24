"""
Main data sanitizing class, consisting of three steps:
1. Type coercion (if set)
2. Type validation
3. Additionally annotated validation
"""
from __future__ import annotations

import datetime as dt

from bluejayson.sanitizers._core import SanitizeRunner
from bluejayson.sanitizers._custom import boolean_flag

DEFAULT_DISPATCHER = SanitizeRunner({
    dt.datetime: dt.datetime.fromisoformat,
    dt.date: dt.date.fromisoformat,
    dt.time: dt.time.fromisoformat,
    bool: boolean_flag,
    # TODO: add more data coercion functions for parametric types
})
