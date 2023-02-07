from dataclasses import dataclass
from typing import Optional
from codex.lang.types import Type
from codex.lang.std import StandardModule


@dataclass
class LanguageInfo:
    """
    Represents metadata for a language.
    """

    display_name: str
    source_file_extension: str
    description: str


class ModuleBinding:
    module: StandardModule

    analogous_module: Optional[str]
    """
    A module in the language's standard library that is analogous to this module.
    For instance, the analogous language module for the Codex `math` module in C is `math.h`.

    Some languages have these functions built-in, so this field is optional. For instance,
    the analogous language module for the Codex `json` module in Python is `json`, but
    in JavaScript, there is no analogous module, since JSON is built-in.
    """

    polyfill: Optional[str]
    """
    Any source code that should be included in the generated code to polyfill the functionality
    of this module.
    """

    type_bindings: dict[Type, str]
    """
    A mapping from Codex types to language-specific type expressions.
    """

    def __init__(
        self,
        module: StandardModule,
        *args,
        analogous_module: Optional[str] = None,
        polyfill: Optional[str] = None,
        type_bindings: Optional[dict[Type, str]] = None,
    ) -> None:
        self.module = module
        self.analogous_module = analogous_module
        self.polyfill = polyfill
        self.type_bindings = type_bindings or {}


class StandardLibraryBinding:
    """
    Represents functionality for generating language-specific code for Codex's standard library
    imports.
    """

    _module_bindings: dict[StandardModule, ModuleBinding]
    _unsupported_modules: set[StandardModule]

    def __init__(self) -> None:
        self._module_bindings = {}
        self._unsupported_modules = set()

    def add_module_binding(self, module_binding: ModuleBinding):
        self._module_bindings[module_binding.module] = module_binding

        return self  # For chaining

    def add_unsupported_module(self, module: StandardModule):
        self._unsupported_modules.add(module)

        return self  # For chaining

    def is_module_supported(self, module: StandardModule) -> bool:
        """
        Return `True` if the given module is supported, even if no binding was explicitly defined.
        Return `False` if the given module is unsupported.
        """

        return module not in self._unsupported_modules

    def get_module_binding(self, module: StandardModule) -> Optional[ModuleBinding]:
        """
        Return the module binding for the given standard module. If no binding was explicitly
        defined for the given module, then return a special `StandardModuleBinding` instance
        with `None` for all fields.

        If the given module is unsupported, then return `None`.
        """

        if not self.is_module_supported(module):
            return None

        return self._module_bindings.get(module, ModuleBinding(module))


class LanguageBinding:
    """
    Represents functionality for generating language-specific code.
    """

    name: str
    info: LanguageInfo
    stdlib_binding: StandardLibraryBinding

    def __init__(
        self, name: str, info: LanguageInfo, stdlib_binding: StandardLibraryBinding
    ) -> None:
        self.name = name
        self.info = info
        self.stdlib_binding = stdlib_binding

    def generate_import(self, module: str) -> str:
        """
        Return a language-specific import statement for the given module.

        Example:
        ```
        cpp = LanguageBinding(...)
        cpp.generate_import("vector") # "#include <vector>"
        ```
        """

        raise NotImplementedError

    def generate_type_expr(self, type: Optional[Type]) -> str:
        """
        Return a language-specific type expression for the given Codex type.

        Example:
        ```
        cpp = LanguageBinding(...)
        cpp.generate_type_expr(Int) # "int"
        cpp.generate_type_expr(Array(Int)) # "vec<int>"
        ```
        """

        raise NotImplementedError

    def generate_incomplete_variable_assignment(self, name: str, type: Optional[Type]) -> str:
        """
        Return a language-specific incomplete variable assignment for the given name and type.

        Example:
        ```
        cpp = LanguageBinding(...)
        cpp.generate_incomplete_variable_assignment("x", Int) # "int x = "
        cpp.generate_incomplete_variable_assignment("x", Array(Int)) # "vec<int> x = "
        ```
        """

        raise NotImplementedError

    def generate_variable_assignment(self, name: str, type: Optional[Type], value: str) -> str:
        """
        Return a language-specific variable assignment for the given name, type, and value.
        ```
        cpp = LanguageBinding(...)
        cpp.generate_variable_assignment("x", Int, "5") # "int x = 5"
        ```
        """

        raise NotImplementedError

    def generate_single_line_comment(self, text: str) -> str:
        """
        Return a language-specific single-line comment for the given text.

        Example:
        ```
        cpp = LanguageBinding(...)
        cpp.generate_single_line_comment("Hello, world!") # "// Hello, world!"
        ```
        """

        raise NotImplementedError

    def generate_multi_line_comment(self, text: str) -> str:
        """
        Return a language-specific multi-line comment for the given text.

        Example:
        ```
        cpp = LanguageBinding(...)
        cpp.generate_multi_line_comment("Hello, world!") # "/* Hello, world! */"
        ```
        """

        raise NotImplementedError

    def generate_function_declaration(
        self,
        name: str,
        return_type: Optional[Type],
        params: list[tuple[str, Optional[Type]]],
        body: str,
    ) -> str:
        """
        Return a language-specific function declaration for the given name, return type, parameters,
        and body.

        Example:
        ```
        cpp = LanguageBinding(...)
        cpp.generate_function_declaration("main", None, [], "return 0;") # "int main() { return 0; }"
        ```
        """

        raise NotImplementedError
