from __future__ import annotations

import pytest  # noqa

from bluejayson.validators import Predicate, ValidationFailed


@pytest.mark.parametrize("validator,value", [
    (Predicate(lambda x: x >= 0), 3),
    (Predicate(lambda x: x, strict=False), "hello"),
    (Predicate(lambda x: x == "cool"), "cool"),
])
def test_validator_pass(validator, value):
    assert validator.validate(value)
    assert validator(value)


@pytest.mark.parametrize("validator,value,error_code", [
    (Predicate(lambda x: x >= 0), -2, 'not_satisfied'),
    (Predicate(lambda x: x, strict=False), 0, 'not_satisfied'),
    (Predicate(lambda x: x == "cool"), 300, 'not_satisfied'),
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
