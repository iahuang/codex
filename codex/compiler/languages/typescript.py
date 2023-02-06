from codex.compiler.codex_types import TYPE_ARRAY, TYPE_INT, TYPE_MAP, TYPE_STRING, Type
from codex.compiler.language_context import (
    OMIT_UNKNOWN_GENERIC,
    BaseLanguageContext,
    LanguageTypeNameMapping,
)
from codex.util.strings import indented


class TypescriptLanguageContext(BaseLanguageContext):
    def __init__(self) -> None:
        mapping = (
            LanguageTypeNameMapping()
            .add_mapping(TYPE_INT, "number")
            .add_mapping(TYPE_ARRAY, "Array")
            .add_mapping(TYPE_MAP, "Map")
            .set_unknown_generic_behavior(OMIT_UNKNOWN_GENERIC)
        )

        super().__init__(
            name="typescript",
            display_name="Typescript",
            source_file_extension="ts",
            type_mapping=mapping,
        )

    def generate_variable_declaration(self, variable_name: str, type: Type) -> str:
        return f"{variable_name}: {self.type_mapping.get_type_repr(type)}"

    def generate_variable_decl_assignment(self, variable_name: str, type: Type, value: str) -> str:
        return f"{variable_name}: {self.type_mapping.get_type_repr(type)} = {value}"

    def generate_single_line_comment(self, comment: str) -> str:
        return "// " + comment

    def generate_multi_line_comment(self, comment: str) -> str:
        escaped = comment.replace("*/", "* /")

        return f"/*\n{indented(escaped, 2)}\n*/"
