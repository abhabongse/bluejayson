"""
Utility functions related to :mod:`typing` package.
"""
from __future__ import annotations


def strip_annotation(dtype):
    """
    Strips the annotation from a given type.
    Adapted from https://github.com/python/cpython/blob/3.9/Lib/typing.py
    """
    try:
        from typing_extensions import _AnnotatedAlias
    except ImportError:
        pass
    else:
        if isinstance(dtype, _AnnotatedAlias):
            return strip_annotation(dtype.__origin__)
    try:
        from typing import _GenericAlias
    except ImportError:
        pass
    else:
        if isinstance(dtype, _GenericAlias):
            stripped_args = tuple(strip_annotation(a) for a in dtype.__args__)
            if stripped_args == dtype.__args__:
                return dtype
            return dtype.copy_with(stripped_args)
    try:
        from typing import GenericAlias
    except ImportError:
        pass
    else:
        if isinstance(dtype, GenericAlias):
            stripped_args = tuple(strip_annotation(a) for a in dtype.__args__)
            if stripped_args == dtype.__args__:
                return dtype
            return GenericAlias(dtype.__origin__, stripped_args)
    return dtype
