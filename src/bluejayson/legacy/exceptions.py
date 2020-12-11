from __future__ import annotations


class BlueJaysonError(Exception):
    pass


class SanitizationError(BlueJaysonError):
    pass


class ValidationError(SanitizationError):
    pass


class ParsingError(BlueJaysonError):
    pass
