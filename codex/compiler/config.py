import os
from dataclasses import dataclass
from codex.compiler.targets import is_language_supported


class CompilerConfigError(Exception):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message

        super().__init__(message)


@dataclass
class CompilerConfig:
    target_language_name: str
    """
    See codex.compiler.languages for a list of supported languages.
    """

    openai_key: str
    """
    See https://beta.openai.com/docs/api-reference/authentication for more information.
    """

    temperature: float = 0.05
    """
    Temperature for OpenAI Codex. Must be between 0.0 and 1.0.
    """


def validate_config(config: CompilerConfig) -> None:
    """
    Validate the given compiler configuration. Raise a CompilerConfigError if the configuration
    is invalid.
    """

    # verify that the language name is valid
    if not is_language_supported(config.target_language_name):
        raise CompilerConfigError(
            f'Language "{config.target_language_name}" is not supported or does not exist. Use --list-languages to see a list of supported languages.'
        )

    # verify that API key has been provided
    if not config.openai_key:
        raise CompilerConfigError("No OpenAI API key provided")

    # verify that temperature is valid
    if config.temperature < 0.0 or config.temperature > 1.0:
        raise CompilerConfigError("Temperature must be between 0.0 and 1.0")
