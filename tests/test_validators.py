from __future__ import annotations

import pytest  # noqa

from bluejayson.validators import Equal, Predicate, Range, ValidationFailed


@pytest.mark.parametrize("validator,value", [
    (Predicate(lambda x: x >= 0), 3),
    (Predicate(lambda x: x, strict=False), "hello"),
    (Predicate(lambda x: x == "cool"), "cool"),
    (Equal(10), 10),
    (Equal(0j), 0.00),
    (Equal("none"), "none"),
    (Equal({0, 1, 2}), {n % 3 for n in range(10)}),
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
])
def test_validator_pass(validator, value):
    assert validator.validate(value)
    assert validator(value)


@pytest.mark.parametrize("validator,value,error_code", [
    (Predicate(lambda x: x >= 0), -2, 'not_satisfied'),
    (Predicate(lambda x: x, strict=False), 0, 'not_satisfied'),
    (Predicate(lambda x: x == "cool"), 300, 'not_satisfied'),
    (Equal(10), -10, 'not_matched'),
    (Equal(0j), 1.e-100, 'not_matched'),
    (Equal(float("nan")), float("nan"), 'not_matched'),
    (Equal({1, 2, 3}), {1, 3, 5}, 'not_matched'),
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
])
def test_validator_failed(validator, value, error_code):
    with pytest.raises(ValidationFailed) as exc_info:
        validator.validate(value)
    assert exc_info.value.error_code == error_code
    assert not validator(value)


@pytest.mark.parametrize("validator_constructor,exc_cls", [
    (lambda: Predicate(lambda: None), TypeError),
    (lambda: Predicate(lambda _x, _y: None), TypeError),
    (lambda: Range(min=0, min_inclusive=1), TypeError),
    (lambda: Range(max=100, max_inclusive=1), TypeError),
])
def test_validator_setup_error(validator_constructor, exc_cls):
    with pytest.raises(exc_cls):
        validator_constructor()


@pytest.mark.parametrize("validator,value,exc_cls", [
    (Predicate(lambda x: x >= 0), "hello", TypeError),
    (Predicate(lambda x: x), "hello", TypeError),
    (Range(min=-12, max=-6, absorb_cmp_error=False), "colony", TypeError),
    (Range(min=(1,), absorb_cmp_error=False), 2, TypeError),
])
def test_validator_runtime_error(validator, value, exc_cls):
    with pytest.raises(exc_cls):
        validator.validate(value)
    with pytest.raises(exc_cls):
        validator(value)
