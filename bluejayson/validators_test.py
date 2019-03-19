import pytest

from bluejayson import validators
from bluejayson.exceptions import ValidationError


def test_validate_is_exactly():
    v = validators.is_exactly(12)
    assert v.sanitize(12) == 12
    with pytest.raises(ValidationError):
        v.sanitize(24)

    v = validators.is_exactly("bluejay")
    assert v.sanitize("bluejay") == "bluejay"
    with pytest.raises(ValidationError):
        v.sanitize("mockingjay")


def test_validate_upper_bound():
    v = validators.upper_bound(100)
    assert v.sanitize(60) == 60
    assert v.sanitize(100) == 100
    with pytest.raises(ValidationError):
        v.sanitize(120)

    v = validators.upper_bound(200, inclusive=False)
    assert v.sanitize(150) == 150
    with pytest.raises(ValidationError):
        v.sanitize(200)
    with pytest.raises(ValidationError):
        v.sanitize(240)


def test_validate_lower_bound():
    v = validators.lower_bound(20)
    assert v.sanitize(60) == 60
    assert v.sanitize(20) == 20
    with pytest.raises(ValidationError):
        v.sanitize(15)

    v = validators.lower_bound(44, inclusive=False)
    assert v.sanitize(55) == 55
    with pytest.raises(ValidationError):
        v.sanitize(44)
    with pytest.raises(ValidationError):
        v.sanitize(33)


def test_validate_between():
    v = validators.between(1500, 2500)
    assert v.sanitize(2000) == 2000
    assert v.sanitize(1500) == 1500
    assert v.sanitize(2500) == 2500
    with pytest.raises(ValidationError):
        v.sanitize(1200)
    with pytest.raises(ValidationError):
        v.sanitize(3600)

    v = validators.between(1500, 2500, inclusive=False, upper_inclusive=True)
    assert v.sanitize(2000) == 2000
    with pytest.raises(ValidationError):
        v.sanitize(1500)
    assert v.sanitize(2500) == 2500
    with pytest.raises(ValidationError):
        v.sanitize(1200)
    with pytest.raises(ValidationError):
        v.sanitize(3600)

    v = validators.between(1500, 2500, upper_inclusive=False)
    assert v.sanitize(2000) == 2000
    assert v.sanitize(1500) == 1500
    with pytest.raises(ValidationError):
        v.sanitize(2500)
    with pytest.raises(ValidationError):
        v.sanitize(1200)
    with pytest.raises(ValidationError):
        v.sanitize(3600)


def test_validate_max_length():
    v = validators.max_length(5)
    assert v.sanitize("hi") == "hi"
    assert v.sanitize("hello") == "hello"
    with pytest.raises(ValidationError):
        v.sanitize("bonjour")

    v = validators.max_length(1)
    assert v.sanitize([]) == []
    assert v.sanitize(["alone"]) == ["alone"]
    with pytest.raises(ValidationError):
        v.sanitize(["first", "second"])


def test_validate_min_length():
    v = validators.min_length(2)
    assert v.sanitize("hi") == "hi"
    assert v.sanitize("hello") == "hello"
    with pytest.raises(ValidationError):
        v.sanitize("")

    v = validators.min_length(1)
    assert v.sanitize(["alone"]) == ["alone"]
    assert v.sanitize(["first", "second"]) == ["first", "second"]
    with pytest.raises(ValidationError):
        v.sanitize([])


def test_validate_length_between():
    v = validators.length_between(1, 2)
    assert v.sanitize("a") == "a"
    assert v.sanitize("bc") == "bc"
    with pytest.raises(ValidationError):
        v.sanitize("")
    with pytest.raises(ValidationError):
        v.sanitize("def")
    assert v.sanitize(["alone"]) == ["alone"]
    assert v.sanitize(["first", "second"]) == ["first", "second"]
    with pytest.raises(ValidationError):
        v.sanitize([])
    with pytest.raises(ValidationError):
        v.sanitize(["r", "g", "b"])
