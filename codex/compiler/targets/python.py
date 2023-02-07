from typing import Optional
from codex.compiler.language_binding import (
    LanguageInfo,
    StandardLibraryBinding,
    LanguageBinding,
    ModuleBinding,
)
from codex.lang.std import StandardLibrary, StdLibTypes
from codex.lang.types import Type
from codex.util.strings import indented

info = LanguageInfo(
    display_name="Python 3",
    source_file_extension="py",
    description="A popular, high-level, general-purpose programming language. OpenAI's Codex model is most capable with generating Python, and Python is the recommended language for most use cases.",
)

stdlib_binding = (
    StandardLibraryBinding()
    .add_module_binding(ModuleBinding(StandardLibrary.Math, analogous_module="math"))
    .add_module_binding(ModuleBinding(StandardLibrary.JSON, analogous_module="json"))
    .add_module_binding(ModuleBinding(StandardLibrary.Random, analogous_module="random"))
    .add_module_binding(
        ModuleBinding(
            StandardLibrary.Linalg,
            polyfill="import numpy as np",
            type_bindings={StdLibTypes.Matrix: "np.ndarray"},
        )
    )
)


class PythonLanguageBinding(LanguageBinding):
    def __init__(self) -> None:
        super().__init__(
            name="python3",
            info=info,
            stdlib_binding=stdlib_binding,
        )

    def generate_import(self, module: str) -> str:
        return f"import {module}"

    def generate_single_line_comment(self, text: str) -> str:
        return f"# {text}"

    def generate_multi_line_comment(self, text: str) -> str:
        escaped = text.replace('"""', '\\"\\"\\"')

        return f'"""{escaped}"""'

    def generate_incomplete_variable_assignment(self, name: str, type: Type) -> str:
        return f"{name} = "

    def generate_variable_assignment(self, name: str, type: Type, value: str) -> str:
        return f"{name} = {value}"

    def generate_function_declaration(
        self,
        name: str,
        return_type: Optional[Type],
        params: list[tuple[str, Optional[Type]]],
        body: str,
    ) -> str:
        param_str = ", ".join(name for name, _ in params)
        return f"def {name}({param_str}):\n{indented(body, 4)}"
