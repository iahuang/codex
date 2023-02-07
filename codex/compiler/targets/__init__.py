from codex.compiler.language_binding import LanguageBinding
from codex.compiler.targets.python import PythonLanguageBinding

LANGUAGE_REGISTRY: list[LanguageBinding] = [
    PythonLanguageBinding(),
]


def get_language_binding(language_name: str) -> LanguageBinding:
    """
    Get a language binding by name (case-insensitive).
    If no language binding is found, a ValueError is raised.
    """

    for language in LANGUAGE_REGISTRY:
        if language.name.lower() == language_name.lower():
            return language

    raise ValueError(f"Language {language_name} is not supported")


def is_language_supported(language_name: str) -> bool:
    """
    Return `True` if a language binding exists for the given language name
    (case-insensitive).
    """

    for language in LANGUAGE_REGISTRY:
        if language.name.lower() == language_name.lower():
            return True

    return False
