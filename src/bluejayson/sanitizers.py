from __future__ import annotations

from typing import List, Union


class Sanitizer:
    """
    A sanitizer validates and cleans up native Python values. It is invoked in one
    of the following two ways:

    1. It is called when a new Schema instance is created directly using the
       constructor.
    2. It is called after an instance is created by parsing a JSON-structured
       object.
    """

    def sanitize(self, value):
        """
        Perform all kinds of validation and sanitization on the given value. This
        function returns the value that has been sanitized. Otherwise it should
        raise an Exception describing an error.
        """
        return value

    def __call__(self, value):
        """Alias for :py:meth:`sanitize` method."""
        return self.sanitize(value)

    @staticmethod
    def concat(left_sanitizer: Union['Sanitizer', 'SanitizerChain'],
               right_sanitizer: Union['Sanitizer', 'SanitizerChain']):
        """
        Chaining all sanitizers together into a sequence.

        Args:
            left_sanitizer:
            right_sanitizer:
                Left and right operand of sanitizer chaining.

        Returns:
            New sanitizer chain by concatenating two sanitizers.
        """
        new_chain = []

        both_operands = (left_sanitizer, right_sanitizer)
        for operand in both_operands:
            if isinstance(operand, SanitizerChain):
                new_chain.extend(operand.chain)
            else:
                new_chain.append(operand)

        return SanitizerChain(chain=new_chain)

    def __matmul__(self, other: 'Sanitizer'):
        return self.concat(self, other)

    def __rmatmul__(self, other: 'Sanitizer'):
        return self.concat(other, self)


class SanitizerChain(Sanitizer):
    """
    A chain (or a sequence) of sanitizers resulting by concatenating together two
    sanitizers (which includes sanitizer chains itself).

    Attributes:
        chain: A sequence of sanitizers.
    """

    def __init__(self, chain: List[Sanitizer]):
        self.chain = chain

    def sanitize(self, value):
        for sanitizer in self.chain:
            value = sanitizer.sanitize(value)
        return value
