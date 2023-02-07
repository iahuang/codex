from typing import Optional
from codex.lang.types import Type


class StandardModule:
    name: str
    """
    Module name as it appears under the `using` directive.
    """

    description: str
    """
    A brief overview of what this module provides.
    """

    keywords: list[str]
    """
    If this module is not included by default, then the compiler will warn the user if any of
    these keywords are used in the code. Case-insensitive.
    """

    include_by_default: bool
    """
    If `True`, then this module is included by default. If `False`, then the user must explicitly
    include this module in their code using the `using` directive.
    """

    module_types: list[Type]

    def __init__(
        self,
        name: str,
        *args,
        description: str,
        keywords: list[str] = [],
        include_by_default: bool = False,
        module_types: list[Type] = [],
    ) -> None:
        self.name = name
        self.description = description
        self.keywords = keywords
        self.include_by_default = include_by_default
        self.module_types = module_types

    def __hash__(self) -> int:
        """
        Allow this class to be used as a key in a dictionary.
        """

        return hash(self.name)


class StdLibTypes:
    Matrix = Type("matrix")
    Array = Type("array")


class StandardLibrary:
    """
    A collection of all standard modules.
    """

    Array = StandardModule(
        "array",
        description="Provides a generic array type.",
        keywords=["array", "vector", "list"],
        include_by_default=True,
        module_types=[StdLibTypes.Array],
    )

    Math = StandardModule(
        "math",
        description="Provides math functions.",
        keywords=["math", "sqrt", "cos", "sin", "tan", "cosine", "sine", "tangent"],
        include_by_default=True,
    )

    FileSystem = StandardModule(
        "fs",
        description="Provides functions for reading and writing to files.",
    )

    JSON = StandardModule(
        "json",
        description="Provides functions for reading and writing JSON.",
        keywords=["json"],
    )

    Random = StandardModule(
        "random",
        description="Provides functions for generating random numbers.",
        keywords=["random", "rand", "randomize"],
    )

    Linalg = StandardModule(
        "linalg",
        description="Provides functions for linear algebra and matrix operations.",
        keywords=["matrix", "2d array", "nd array"],
        module_types=[StdLibTypes.Matrix],
    )


def get_standard_module(name: str) -> Optional[StandardModule]:
    """
    Search `StandardLibrary` for a module with the given name. If none is found, return `None`.
    """

    for module in StandardLibrary.__dict__.values():
        if isinstance(module, StandardModule) and module.name == name:
            return module

    return None


def get_all_standard_modules() -> list[StandardModule]:
    """
    Return a list of all standard modules.
    """

    return [
        module for module in StandardLibrary.__dict__.values() if isinstance(module, StandardModule)
    ]
