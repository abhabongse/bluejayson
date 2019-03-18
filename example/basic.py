from typing import List, Dict

from bluejayson import BaseSchema, fields, validators


class FirstSchema(BaseSchema):
    name: str = fields.StrField(sanitizer=validators.MaxLength(limit=255))
    age: int = fields.IntField(sanitizer=validators.ValidatorFunc(lambda x: x >= 0, "must be non-negative"))
    married: bool = fields.BoolField(default=True)
    friends: Dict[str, int] = fields.DictField(int)
    inventory: List[int] = fields.ListField(int)


class SecondSchema(FirstSchema):
    occupation: str = fields.StrField()


# Check all defined fields for each Schema
print(FirstSchema.bjs_all_fields)
print(SecondSchema.bjs_all_fields)

# Initialize an instance
person = FirstSchema(name="John", age=20, married=False, friends={'Mary': 21}, inventory=[7])
another_person = SecondSchema(name="Lilly", age=19, friends={}, inventory=[2, 3])
