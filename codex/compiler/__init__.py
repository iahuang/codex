import os
from dataclasses import dataclass
from codex.parser.ast import Module, ActionStatementNode
from codex.compiler.language_context import BaseLanguageContext
from codex.compiler.languages import is_language_supported, get_language_context
from codex.compiler.prompt_generation import PromptGenerator
from codex.compiler.openai_codex import OpenAICodex
from codex.util.strings import StringBuilder
from codex.util.fs import write_file


@dataclass
class CompilerConfig:
    language_name: str
    """
    See codex.compiler.languages for a list of supported languages.
    """

    output_path: str
    """
    Refers to a file into which the generated code will be written.
    Should not include a file extension.
    """

    openai_key: str
    """
    See https://beta.openai.com/docs/api-reference/authentication for more information.
    """

    temperature: float = 0.05
    """
    Temperature for OpenAI Codex. Must be between 0.0 and 1.0.
    """


class CompilerConfigError(Exception):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message

        super().__init__(message)


def validate_config(config: CompilerConfig) -> None:
    """
    Validate the given compiler configuration. Raise a CompilerConfigError if the configuration
    is invalid.
    """

    # check that output path is not a directory
    if os.path.exists(config.output_path) and os.path.isdir(config.output_path):
        raise CompilerConfigError("Output file path already refers to a directory.")

    # verify that the language name is valid
    if not is_language_supported(config.language_name):
        raise CompilerConfigError(
            f'Language "{config.language_name}" is not supported or does not exist. Use --list-languages to see a list of supported languages.'
        )

    # verify that API key has been provided
    if not config.openai_key:
        raise CompilerConfigError("No OpenAI API key provided")

    # verify that temperature is valid
    if config.temperature < 0.0 or config.temperature > 1.0:
        raise CompilerConfigError("Temperature must be between 0.0 and 1.0")


class Compiler:
    config: CompilerConfig
    module: Module
    _output: StringBuilder
    _lang: BaseLanguageContext
    _prompt_generator: PromptGenerator
    _codex: OpenAICodex

    def __init__(self, module: Module, config: CompilerConfig) -> None:
        validate_config(config)

        self.module = module
        self.config = config
        self._output = StringBuilder()

        self._lang = get_language_context(self.config.language_name)
        self._prompt_generator = PromptGenerator(language_context=self._lang)
        self._codex = OpenAICodex(api_key=config.openai_key, model="code-davinci-002")

    def write_to_output(self, text: str) -> None:
        self._output.writeln(text)

    def compile(self) -> None:
        for node in self.module.children:
            if isinstance(node, ActionStatementNode):
                prompt = self._prompt_generator.action_statement(node)
                generated_code = self._codex.generate_insertion(
                    prompt=prompt,
                    temperature=self.config.temperature,
                    max_tokens=100,
                )

                self.write_to_output(generated_code)

        ext = self._lang.language_source_file_extension
        write_file(self.config.output_path + "." + ext, self._output.get_data())
