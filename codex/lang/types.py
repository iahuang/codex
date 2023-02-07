from __future__ import annotations
from dataclasses import dataclass

UKNOWN_NUM_GENERIC = -1


@dataclass
class TypeBase:
    id: int
    name: str
    primitve: bool
    num_generic_args: int

    def __eq__(self, other: TypeBase) -> bool:
        return self.id == other.id

    def __hash__(self) -> int:
        return self.id


class Type:
    base_type: TypeBase

    user_defined_name: str
    """
    Valid only if `base_type` is `TYPE_USER_DEFINED`.
    """

    generic_parameters: list[Type]

    def __init__(
        self, base_type: TypeBase, user_defined_name: str = "", generic_parameters: list[Type] = []
    ) -> None:
        self.base_type = base_type
        self.user_defined_name = user_defined_name
        self.generic_parameters = generic_parameters

        # Validate arguments

        if base_type == TYPE_USER_DEFINED and user_defined_name == "":
            raise Exception("User defined type must have a name")

    def get_type_name(self) -> str:
        base = self.base_type.name

        if self.base_type == TYPE_USER_DEFINED:
            base = self.user_defined_name

        if self.base_type.num_generic_args > 0:
            base += f"<{', '.join([param.get_type_name() for param in self.generic_parameters])}>"

        return base

    def __eq__(self, other: Type) -> bool:
        return (
            self.base_type == other.base_type
            and self.generic_parameters == other.generic_parameters
        )

TYPE_UNKNOWN = TypeBase(0, "unknown", False, UKNOWN_NUM_GENERIC)
TYPE_BOOL = TypeBase(1, "bool", True, 0)
TYPE_INT = TypeBase(2, "int", True, 0)
TYPE_FLOAT = TypeBase(3, "float", True, 0)
TYPE_STRING = TypeBase(4, "string", True, 0)
TYPE_ARRAY = TypeBase(5, "array", False, 1)
TYPE_MAP = TypeBase(6, "map", False, 2)
TYPE_USER_DEFINED = TypeBase(7, "user_defined", False, UKNOWN_NUM_GENERIC)

Unknown = Type(TYPE_UNKNOWN)
Int = Type(TYPE_INT)
Float = Type(TYPE_FLOAT)
Bool = Type(TYPE_BOOL)
String = Type(TYPE_STRING)
Array = lambda type: Type(TYPE_ARRAY, generic_parameters=[type])
Map = lambda key_type, value_type: Type(TYPE_MAP, generic_parameters=[key_type, value_type])
UserDefined = lambda name: Type(TYPE_USER_DEFINED, user_defined_name=name)

def construct_generic(base: TypeBase, generic_parameters: list[Type]) -> Type:
    """
    Construct a generic type from a base type and a list of generic parameters.
    
    If there are insufficient generic parameters, the remaining parameters are filled with `Unknown`.

    If the base type does not support generics, an exception is raised.
    """

    if base.num_generic_args == UKNOWN_NUM_GENERIC:
        raise Exception(f"Base type {base.name} does not support generics")

    if base.num_generic_args == 0:
        raise Exception(f"Base type {base.name} does not support generics")

    if len(generic_parameters) > base.num_generic_args:
        raise Exception(f"Too many generic parameters for base type {base.name}")

    if len(generic_parameters) < base.num_generic_args:
        generic_parameters += [Unknown] * (base.num_generic_args - len(generic_parameters))

    return Type(base, generic_parameters=generic_parameters)

