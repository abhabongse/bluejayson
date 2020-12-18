from __future__ import annotations

import pytest  # noqa

from bluejayson.validators import Equal, Predicate, ValidationFailed


@pytest.mark.parametrize("validator,value", [
    (Predicate(lambda x: x >= 0), 3),
    (Predicate(lambda x: x, strict=False), "hello"),
    (Predicate(lambda x: x == "cool"), "cool"),
    (Equal(10), 10),
    (Equal(0j), 0.00),
    (Equal("none"), "none"),
    (Equal({0, 1, 2}), {n % 3 for n in range(10)}),
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
])
def test_validator_failed(validator, value, error_code):
    with pytest.raises(ValidationFailed) as exc_info:
        validator.validate(value)
    assert exc_info.value.error_code == error_code
    assert not validator(value)


@pytest.mark.parametrize("validator_constructor,exc_cls", [
    (lambda: Predicate(lambda: None), TypeError),
    (lambda: Predicate(lambda _x, _y: None), TypeError),
])
def test_validator_setup_error(validator_constructor, exc_cls):
    with pytest.raises(exc_cls):
        validator_constructor()


@pytest.mark.parametrize("validator,value,exc_cls", [
    (Predicate(lambda x: x >= 0), "hello", TypeError),
    (Predicate(lambda x: x), "hello", TypeError),
])
def test_validator_runtime_error(validator, value, exc_cls):
    with pytest.raises(exc_cls):
        validator.validate(value)
    with pytest.raises(exc_cls):
        validator(value)
