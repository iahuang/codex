from typing import Optional
import re

from codex.parser.ast import (
    ASTNode,
    Module,
    PromptNode,
    UsingDirectiveNode,
    ActionStatementNode,
    VariableDeclarationNode,
)
from codex.util.strings import StringBuilder

from codex.openai import OpenAI, DAVINCI_MAX_TOKENS

from codex.lang.std import StandardModule, get_standard_module, get_all_standard_modules
from codex.lang.types import (
    TYPE_ARRAY,
    TYPE_BOOL,
    TYPE_FLOAT,
    TYPE_INT,
    TYPE_MAP,
    TYPE_STRING,
    TYPE_UNKNOWN,
    Type,
)

from codex.compiler.language_binding import LanguageBinding
from codex.compiler.targets import get_language_binding
from codex.compiler.config import CompilerConfig
from codex.compiler.codegen import GENERATED, Codegen, SnippetGenerator, CodegenContext


class CompilerError(Exception):
    offending_node: ASTNode
    message: str

    def __init__(self, message: str, offending_node: ASTNode) -> None:
        self.message = message
        self.offending_node = offending_node

        super().__init__(message)


class Compiler:

    module: Module
    """
    The module being compiled.
    """

    config: CompilerConfig
    """
    The configuration object passed to the constructor.
    """

    target: LanguageBinding
    """
    The language binding for the target language.
    """

    _openai: OpenAI
    """
    The OpenAI API wrapper, used for code generation.
    """

    _codegen: Codegen
    """
    The helper class used for generating code snippets.
    """

    _header: StringBuilder
    _program: StringBuilder

    _errors: list[CompilerError]
    _warnings: list[CompilerError]

    _used_modules: set[StandardModule]

    def __init__(self, module: Module, config: CompilerConfig) -> None:
        """
        This constructor does not validate the given module or configuration. The configuration
        may be validated separately using the `validate_config` function of `codex.compiler.config`.
        """

        self.module = module
        self.config = config
        self.target = get_language_binding(config.target_language_name)

        self._openai = OpenAI(config.openai_key)
        self._codegen = Codegen(self.target, prompt_token_limit=DAVINCI_MAX_TOKENS)

        self._header = StringBuilder()
        self._program = StringBuilder()

        self._errors = []
        self._warnings = []

        self._used_modules = set()

    def _reify_snippet(self, snippet_generator: SnippetGenerator) -> str:
        """
        Given a snippet generator, generate a code snippet using the OpenAI Codex API.
        """

        generation = self._openai.generate_code(
            snippet_generator.codex_prompt, self.config.temperature, 150
        )

        return snippet_generator.generation_template.replace(GENERATED, generation)

    def _compile_using_directive(self, node: UsingDirectiveNode) -> None:
        module = get_standard_module(node.module_name)

        if module is None:
            self._errors.append(CompilerError(f"Unknown module '{node.module_name}'", node))
            return

        # ensure that the module is not imported by default
        if module.include_by_default:
            self._warnings.append(
                CompilerError(f"Module '{module.name}' is included by default", node)
            )
            return

        # ensure that the module is supported by the target language
        if not self.target.stdlib_binding.is_module_supported(module):
            self._errors.append(
                CompilerError(
                    f"Module '{module.name}' is not supported by the target language", node
                )
            )
            return

        # ensure that the module is not already imported
        if module in self._used_modules:
            self._warnings.append(
                CompilerError(f"Module '{module.name}' is already imported", node)
            )
            return

        self._include_module(module)

    def _include_module(self, module: StandardModule) -> None:
        """
        Add the language-specific bindings for the given module to the program header.

        This method does not check for duplicate imports and assumes that the module is supported
        by the target language.
        """

        self._used_modules.add(module)

        # get language-specific bindings for the module
        binding = self.target.stdlib_binding.get_module_binding(module)

        assert binding is not None

        # check for a language-specific analog of the module
        if binding.analogous_module is not None:
            self._header.writeln(self.target.generate_import(binding.analogous_module))

        # check for polyfills
        if binding.polyfill is not None:
            self._header.writeln(binding.polyfill)

    def _set_codegen_context(self) -> None:
        """
        Add the program header and body as context for the code generator.
        """

        context = CodegenContext(
            required_context=self._header.to_string(),
            helpful_context=self._program.to_string(),
        )

        self._codegen.set_context(context)

    def _resolve_type(self, type_name: str) -> Optional[Type]:
        """
        Given a type expression such as "int" or "array", return a corresponding Type object.

        Return None if the type expression is invalid.
        """

        BASE_TYPES = [
            TYPE_UNKNOWN,
            TYPE_BOOL,
            TYPE_INT,
            TYPE_FLOAT,
            TYPE_STRING,
            TYPE_ARRAY,
            TYPE_MAP,
        ]

        for base_type in BASE_TYPES:
            if type_name == base_type.name:
                return Type(base_type)

        return None

    def _compile_action_statement(self, node: ActionStatementNode) -> None:
        self._set_codegen_context()
        snippet = self._codegen.generate_action(node.prompt.prompt)
        self._program.writeln(self._reify_snippet(snippet))

    def _compile_variable_declaration(self, node: VariableDeclarationNode) -> None:
        type = self._resolve_type(node.type)

        if type is None:
            self._errors.append(CompilerError(f"Unknown type '{node.type}'", node))
            return

        self._set_codegen_context()
        snippet = self._codegen.generate_variable_decl(
            name=node.variable_name,
            type=type,
            variable_prompt=node.prompt.prompt,
        )
        self._program.writeln(self._reify_snippet(snippet))

    def _check_prompt_for_unincluded_modules(self, node: PromptNode) -> None:
        """
        Check the prompt for keywords that correspond to modules that have not been included
        using the `using` directive. If any are found, add a warning.
        """

        prompt_text = node.prompt.prompt

        for module in get_all_standard_modules():
            if module.include_by_default:
                continue

            for keyword in module.keywords:
                if re.findall(r"\b" + keyword.lower() + r"\b", prompt_text.lower()):
                    self._warnings.append(
                        CompilerError(
                            f'Prompt mentions "{keyword}", but the {module.name} module was not included. Consider adding "using {module.name}" to the top of your file.',
                            node,
                        )
                    )
                    break  # don't add multiple warnings for the same module

    def compile(self) -> None:
        """
        This method does not return anything.
        """

        # include modules that are included by default
        for module in get_all_standard_modules():
            if module.include_by_default:
                self._include_module(module)

        for node in self.module.children:
            if isinstance(node, UsingDirectiveNode):
                self._compile_using_directive(node)
            elif isinstance(node, ActionStatementNode):
                self._check_prompt_for_unincluded_modules(node)

                self._compile_action_statement(node)
            elif isinstance(node, VariableDeclarationNode):
                self._check_prompt_for_unincluded_modules(node)

                self._compile_variable_declaration(node)
            else:
                raise NotImplementedError(f"Cannot compile node of type {type(node).__name__}")

    def get_errors(self) -> list[CompilerError]:
        return self._errors[:]  # copy to prevent mutation

    def get_warnings(self) -> list[CompilerError]:
        return self._warnings[:]  # copy to prevent mutation

    def get_output(self) -> str:
        return self._header.to_string() + "\n\n" + self._program.to_string()
