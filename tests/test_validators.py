from __future__ import annotations

import math
import re

import pytest  # noqa

from bluejayson.validators import InChoices, Length, Match, Predicate, Range, Regexp, ValidationFailed


@pytest.mark.parametrize("validator,value", [
    (Predicate(lambda x: x >= 0), 3),
    (Predicate(lambda x: x, strict=False), "hello"),
    (Predicate(lambda x: x == "cool"), "cool"),
    (Match(10), 10),
    (Match(0j), 0.00),
    (Match("none"), "none"),
    (Match(math.pi, compare=math.isclose), 3.141592653589),
    (Match(math.pi, compare=lambda x, y: 'yes' if math.isclose(x, y) else '', strict=False), 3.141592653589),
    (Match({0, 1, 2}), {n % 3 for n in range(10)}),
    (Range(min=7), 10),
    (Range(max=-3), -5),
    (Range(min=-12, max=-6), -10),
    (Range(min=-12, max=-6), -12),
    (Range(min=-12, max=-6), -6),
    (Range(min=-12, max=-6, min_inclusive=False), -10),
    (Range(min=-12, max=-6, min_inclusive=False), -6),
    (Range(min=-12, max=-6, max_inclusive=False), -10),
    (Range(min=-12, max=-6, max_inclusive=False), -12),
    (Range(min=-12, max=-6, min_inclusive=False, max_inclusive=False), -10),
    (Range(min="elephant", max="hippo"), "giraffe"),
    (Range(min=(3, 10), max=(3, 11)), (3, 10, None)),
    (Length(min=3), list(range(5))),
    (Length(max=7), []),
    (Length(equal=4), "good"),
    (Length(min=7, max=8), "article"),
    (Regexp(r'\w+|\d'), "abc"),
    (Regexp(r'\w+|\d'), "0"),
    (Regexp(re.compile(r'\w+|\d')), "xyz"),
    (Regexp(re.compile(r'\w+|\d')), "7"),
    (Regexp(r'(\d+):(\d+)', post_validate=lambda x, y: int(x) + int(y) == 1801), "1234:567"),
    (Regexp(re.compile(r'\w(\w*)\w'), post_validate=lambda s: s == "bcdef"), "abcdefg"),
    (Regexp(r'(\w+)', post_validate=lambda x: x, strict=False), "foxes"),
    (InChoices(range(10)), 7),
    (InChoices("aeiou"), "e"),
    (InChoices([0, 3, 6, 9], compare=math.isclose), 3 + 1.e-12),
    (InChoices([0, 3, 6, 9], compare=lambda x, y: '' if y == 0 else math.isclose(x, y), strict=False),
     3 + 1.e-12),
])
def test_validator_pass(validator, value):
    assert validator.validate(value)
    assert validator(value)


@pytest.mark.parametrize("validator,value,error_code", [
    (Predicate(lambda x: x >= 0), -2, 'not_satisfied'),
    (Predicate(lambda x: x, strict=False), 0, 'not_satisfied'),
    (Predicate(lambda x: x == "cool"), 300, 'not_satisfied'),
    (Match(10), -10, 'not_matched'),
    (Match(0j), 1.e-100, 'not_matched'),
    (Match(float("nan")), float("nan"), 'not_matched'),
    (Match({1, 2, 3}), {1, 3, 5}, 'not_matched'),
    (Match(math.pi, compare=math.isclose), 3.14159, 'not_matched'),
    (Range(min=7), 4, 'out_of_range'),
    (Range(max=-3), 7, 'out_of_range'),
    (Range(min=-12, max=-6), -24, 'out_of_range'),
    (Range(min=-12, max=-6), 99, 'out_of_range'),
    (Range(min=-12, max=-6, min_inclusive=False), -12, 'out_of_range'),
    (Range(min=-12, max=-6, max_inclusive=False), -6, 'out_of_range'),
    (Range(min=-12, max=-6, min_inclusive=False, max_inclusive=False), -12, 'out_of_range'),
    (Range(min=-12, max=-6, min_inclusive=False, max_inclusive=False), -16, 'out_of_range'),
    (Range(min=-12, max=-6), "colony", 'incomparable'),
    (Range(min=(1,)), 2, 'incomparable'),
    (Length(min=6, max=19), 12, 'uncomputable_length'),
    (Length(min=3), [], 'length_out_of_range'),
    (Length(max=7), "manually", 'length_out_of_range'),
    (Length(equal=4), "not ok", 'length_out_of_range'),
    (Length(min=7, max=8), "data", 'length_out_of_range'),
    (Length(min=7, max=8), "data anomaly", 'length_out_of_range'),
    (Regexp(r'\w+|\d'), 0, 'not_string'),
    (Regexp(r'\w+|\d'), "no more tests", 'not_matched'),
    (Regexp(re.compile(r'\w+|\d')), -789, 'not_string'),
    (Regexp(re.compile(r'\w+|\d')), "cool beans", 'not_matched'),
    (Regexp(r'(\d+):(\d+)', post_validate=lambda x, y: int(x) + int(y) == 1801), 1234567, 'not_string'),
    (Regexp(r'(\d+):(\d+)', post_validate=lambda x, y: int(x) + int(y) == 1801), "1234567", 'not_matched'),
    (Regexp(r'(\d+):(\d+)', post_validate=lambda x, y: int(x) + int(y) == 1801), "123:4567", 'not_satisfied'),
    (InChoices([]), 1729, 'not_found'),
    (InChoices("aeiou"), "ei", 'not_found'),
    (InChoices([0, 3, 6, 9]), 3 + 1.e-12, 'not_found'),
])
def test_validator_failed(validator, value, error_code):
    with pytest.raises(ValidationFailed) as exc_info:
        validator.validate(value)
    assert exc_info.value.error_code == error_code
    assert not validator(value)


@pytest.mark.parametrize("validator_constructor,exc_cls", [
    (lambda: Range(min=0, min_inclusive=1), TypeError),
    (lambda: Range(max=100, max_inclusive=0), TypeError),
    (lambda: Length(min=(5, 10)), TypeError),
    (lambda: Length(max="3"), TypeError),
    (lambda: Length(equal=[]), TypeError),
    (lambda: Length(min=0, equal=0), ValueError),
    (lambda: Length(max=20, equal=3), ValueError),
    (lambda: Regexp(1), TypeError),
    (lambda: Regexp('('), re.error),
    (lambda: InChoices(10), TypeError),
])
def test_validator_setup_error(validator_constructor, exc_cls):
    with pytest.raises(exc_cls):
        validator_constructor()


@pytest.mark.parametrize("validator,value,exc_cls", [
    (Predicate(lambda: True), "hello", TypeError),
    (Predicate(lambda _x, _y: True), "hi", TypeError),
    (Predicate(lambda *, _: True), "hello again", TypeError),
    (Predicate(lambda x: x >= 0), "hello 123", TypeError),
    (Predicate(lambda x: x), "hello 456", TypeError),
    (Match(math.pi, compare=math.isclose), "pqrs", TypeError),
    (Match(math.pi, compare=lambda x, y: 'yes' if math.isclose(x, y) else ''), 3.141592653589, TypeError),
    (Range(min=-12, max=-6, absorb_cmp_error=False), "colony", TypeError),
    (Range(min=(1,), absorb_cmp_error=False), 2, TypeError),
    (Length(min=6, max=19, absorb_len_error=False), 12, TypeError),
    (Regexp(r'(\w+)', post_validate="maybe"), 'cool', TypeError),
    (Regexp(r'(\w+)', post_validate=lambda: True), 'cooler', TypeError),
    (Regexp(r'(\w+)', post_validate=lambda _: "yes"), 'coolest', TypeError),
    (InChoices([0, 3, 6, 9], compare=lambda x, y: '' if y == 0 else math.isclose(x, y)),
     3 + 1.e-12, TypeError),
])
def test_validator_runtime_error(validator, value, exc_cls):
    with pytest.raises(exc_cls):
        validator.validate(value)
    with pytest.raises(exc_cls):
        validator(value)
