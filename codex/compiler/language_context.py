from typing import Optional
from codex.compiler.codex_types import TYPE_UNKNOWN, TYPE_USER_DEFINED, Type, TypeBase

OMIT_UNKNOWN_GENERIC = 0
USE_UNKNOWN_MAPPING = 1


class LanguageTypeNameMapping:
    """
    Represents language-specific mapping from Codex types to language-specific type names.

    For instance, Codex `int` would be mapped to `int` in C++, but `i32` in Rust. By default,
    type names are the same as the Codex type names.

    By default, generic type brackets are `<` and `>`.

    By default, unknown types are not mapped to anything,
    and when `get_language_specific_type_representation` is called, `None` is returned.

    If an unknown type is encountered as a generic parameter, the behavior can be changed
    by calling `set_unknown_in_generic_behavior`. By default, the behavior is `USE_UNKNOWN_MAPPING`,
    indicating that the unknown type should be mapped to a language-specific name, if possible.

    If no mapping is found for an unknown type in this case, an exception is raised.
    """

    _mapping: dict[TypeBase, str]
    _generic_type_brackets_open: str
    _generic_type_brackets_close: str

    _unknown_in_generic_behavior: int

    def __init__(self) -> None:
        self._mapping = {}
        self._generic_type_brackets_open = "<"
        self._generic_type_brackets_close = ">"

        self._unknown_in_generic_behavior = USE_UNKNOWN_MAPPING

    def add_mapping(self, type: TypeBase, name: str):
        """
        Adds a mapping from a Codex type to a language-specific type name.

        Type mappings for `TYPE_USER_DEFINED` is not allowed.

        Example:
        ```
        java_mapping = LanguageTypeNameMapping()
        java_mapping.add_mapping(TYPE_INT, "int")
        java_mapping.add_mapping(TYPE_STRING, "String")

        cpp_mapping = LanguageTypeNameMapping()
        cpp_mapping.add_mapping(TYPE_INT, "int")
        cpp_mapping.add_mapping(TYPE_STRING, "std::string")
        ```
        """

        if type == TYPE_USER_DEFINED:
            raise ValueError("Cannot map user-defined types to language-specific names")

        self._mapping[type] = name

        # Allow chaining
        return self

    def set_generic_type_brackets(self, open: str, close: str):
        """
        By default generic type brackets are `<` and `>`. This method allows to change them.

        Example:
        ```
        java_mapping = LanguageTypeNameMapping()
        java_mapping.set_generic_type_brackets("<", ">")

        python_mapping = LanguageTypeNameMapping()
        python_mapping.set_generic_type_brackets("[", "]")
        ```
        """

        self._generic_type_brackets_open = open
        self._generic_type_brackets_close = close

        # Allow chaining
        return self

    def set_unknown_generic_behavior(self, behavior: int):
        self._unknown_in_generic_behavior = behavior

        return self

    def get_type_repr(self, type: Type) -> Optional[str]:
        """
        Return the language-specific type representation for the given Codex type.

        Example:
        ```
        java_mapping = LanguageTypeNameMapping()
        java_mapping.add_mapping(TYPE_INT, "int")
        java_mapping.add_mapping(TYPE_ARRAY, "ArrayList")

        array_of_int = Array(Int)

        # Prints "ArrayList<int>"
        print(java_mapping.get_language_specific_type_representation(array_of_int))
        ```

        If the type is unknown, and `set_unknown_generic_behavior` is set to `OMIT_UNKNOWN_GENERIC`,
        the generic type arguments are omitted.

        Example:
        ```
        python_mapping = LanguageTypeNameMapping()
        python_mapping.add_mapping(TYPE_ARRAY, "list")
        python_mapping.set_unknown_generic_behavior(OMIT_UNKNOWN_GENERIC)

        # Prints "list"
        print(python_mapping.get_language_specific_type_representation(Array(Unknown)))
        ```
        """

        base_name = type.get_type_name()

        if type.base_type == TYPE_UNKNOWN:
            # check if unknown mapping exists
            if TYPE_UNKNOWN not in self._mapping:
                return None

        if type.base_type == TYPE_USER_DEFINED:
            base_name = type.user_defined_name

        if type.base_type in self._mapping:
            base_name = self._mapping[type.base_type]

        # append generic type arguments

        if type.generic_parameters:
            parameters: list[str] = []

            for param in type.generic_parameters:
                param_repr = self.get_type_repr(param)

                if param.base_type == TYPE_UNKNOWN:
                    if self._unknown_in_generic_behavior == OMIT_UNKNOWN_GENERIC:
                        return base_name

                    if param_repr is None:
                        raise ValueError(
                            f"Unknown type encountered in generic type {type}, but no mapping exists for it"
                        )

                assert param_repr is not None

                parameters.append(param_repr)

            return f"{base_name}{self._generic_type_brackets_open}{', '.join(parameters)}{self._generic_type_brackets_close}"

        # if not generic, return base name

        return base_name


def indented(code: str, indentation_spaces: int = 4) -> str:
    """
    Indents the given code by the given number of spaces.

    Example:
    ```
    print(indented("a\\nb\\nc", 2)) # prints "  a\\n  b\\n  c"
    ```
    """

    return "\n".join(" " * indentation_spaces + line for line in code.split("\n"))


class BaseLanguageContext:
    """
    Class for generating language-specific code and prompts for OpenAI Codex.
    """

    language_name: str
    """
    Internal language name, used for identifying the language. For instance, for C++, this is `cpp`.
    """

    language_display_name: str
    """
    Display name for the language. For instance, for C++, this is `C++`.
    """

    language_source_file_extension: str
    """
    Language-specific source file extension. For instance, for Python, this is `py`.
    Does not include the dot.
    """

    type_mapping: LanguageTypeNameMapping

    def __init__(
        self,
        name: str,
        display_name: str,
        source_file_extension: str,
        type_mapping: LanguageTypeNameMapping,
    ) -> None:
        self.language_name = name
        self.language_display_name = display_name
        self.language_source_file_extension = source_file_extension
        self.type_mapping = type_mapping

    def generate_variable_declaration(self, variable_name: str, type: Type) -> str:
        """
        Example:
        ```
        context = BaseLanguageContext("cpp", "C++", LanguageTypeNameMapping())
        context.generate_variable_declaration_stub("x", Int) # "int x;"
        ```
        """

        raise NotImplementedError()

    def generate_variable_decl_assignment(self, variable_name: str, type: Type, value: str) -> str:
        """
        Example:
        ```
        context = BaseLanguageContext("cpp", "C++", LanguageTypeNameMapping())
        context.generate_variable_decl_assignment("x", Int, "5") # "int x = 5;"
        ```
        """

        raise NotImplementedError()

    def generate_single_line_comment(self, comment: str) -> str:
        """
        Example:
        ```
        context = BaseLanguageContext("cpp", "C++", LanguageTypeNameMapping())
        context.generate_single_line_comment("Hello World") # "// Hello World"
        ```
        """

        raise NotImplementedError()

    def generate_multi_line_comment(self, comment: str) -> str:
        """
        Example:
        ```
        context = BaseLanguageContext("cpp", "C++", LanguageTypeNameMapping())
        context.generate_multi_line_comment("Hello World") # "/*\\nHello World\\n*/"
        ```
        """

        raise NotImplementedError()
