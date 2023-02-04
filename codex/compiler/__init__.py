import os
from dataclasses import dataclass
from codex.parser.ast import Module
from codex.compiler.languages import is_language_supported, get_language_context


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
            f'Language "{config.language_name}" is not supported or does not exist.'
        )


class Compiler:
    config: CompilerConfig
    module: Module

    def __init__(self, module: Module, config: CompilerConfig) -> None:
        self.module = module
        self.config = config

    def compile(self) -> None:
        validate_config(self.config)
