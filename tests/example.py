from __future__ import annotations

from typing import Dict, List

from bluejayson import BaseSchema, validators
from bluejayson.legacy import fields


class FirstSchema(BaseSchema):
    name: str = fields.StrField(sanitizer=validators.max_length(limit=255))
    age: int = fields.IntField(
        sanitizer=validators.Validator(lambda x: x >= 0, "must be non-negative"),
    )
    married: bool = fields.BoolField(default=True)
    friends: Dict[str, int] = fields.DictField(int)
    inventory: List[int] = fields.ListField(int)


class SecondSchema(FirstSchema):
    friends: List[str] = fields.ListField(str)
    occupation: str = fields.StrField(sanitizer=validators.is_exactly("student"))


# Check all defined fields for each Schema
print(FirstSchema.bjs_all_fields)
print(SecondSchema.bjs_all_fields)

# Initialize an instance
person = FirstSchema(name="John", age=20, married=False, friends={'Mary': 21}, inventory=[7])
another_person = SecondSchema(name="Lilly", age=19, friends={}, inventory=[2, 3], occupation="student")
