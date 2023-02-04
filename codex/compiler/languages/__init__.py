from codex.compiler.language_context import BaseLanguageContext
from codex.compiler.languages.python import PythonLanguageContext


LANGUAGE_REGISTRY: list[BaseLanguageContext] = [PythonLanguageContext()]


def get_language_context(language_name: str) -> BaseLanguageContext:
    """
    Get a language context by name (case-insensitive).
    If no language context is found, a ValueError is raised.
    """

    for language in LANGUAGE_REGISTRY:
        if language.language_name.lower() == language_name.lower():
            return language

    raise ValueError(f"Language {language_name} is not supported")

def is_language_supported(language_name: str) -> bool:
    """
    Check if a language is supported, i.e. if a language context exists for it.
    """

    for language in LANGUAGE_REGISTRY:
        if language.language_name.lower() == language_name.lower():
            return True
    
    return False

def get_all_languages() -> list[str]:
    """
    Return a list of all supported language names.
    """

    return [language.language_name for language in LANGUAGE_REGISTRY]