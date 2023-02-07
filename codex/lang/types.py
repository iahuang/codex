from __future__ import annotations
from dataclasses import dataclass
from random import randint


def _generate_id() -> int:
    return randint(0, 1000000)


class Type:
    name: str
    _id: int

    def __init__(self, name: str) -> None:
        self.name = name
        self._id = _generate_id()

    def __eq__(self, other: Type) -> bool:
        return self._id == other._id

    def __hash__(self) -> int:
        return self._id


Int = Type("int")
Float = Type("float")
String = Type("string")
Bool = Type("bool")

Void = Type("void")

BASE_TYPES = [Int, Float, String, Bool]
"""
Includes all base types. Does not include `Void`.
"""
