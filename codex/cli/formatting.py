from colorama import Fore, Style
from codex.compiler import CompilerConfigError
from codex.parser.errors import CodexSyntaxError
from codex.util.strings import StringBuilder
from codex.compiler.languages import get_language_context

def red(text: str) -> str:
    """
    Return the given text in red.
    """

    return f"{Fore.RED}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def green(text: str) -> str:
    """
    Return the given text in green.
    """

    return f"{Fore.GREEN}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def yellow(text: str) -> str:
    """
    Return the given text in yellow.
    """

    return f"{Fore.YELLOW}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def blue(text: str) -> str:
    """
    Return the given text in blue.
    """

    return f"{Fore.BLUE}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def format_compilerconfigerror(error: CompilerConfigError) -> str:
    """
    Format the given CompilerConfigError as a colored string.
    """

    return f"{red('configuration error:')} {error.message}"

def format_simple_error(error: str) -> str:
    """
    Format the given error as a colored string.
    """

    return f"{red('error:')} {error}"

def format_syntaxerror(error: CodexSyntaxError) -> str:
    """
    Format the given CodexSyntaxError as a colored string.
    """

    s = StringBuilder()
    s.writeln(f"{red('error:')} {error.message}")

    return s.get_data()

def format_language_list(languages: list[str]) -> str:
    """
    Format the given list of language names as a colored string.
    """

    s = StringBuilder()
    s.writeln(f"{Style.BRIGHT}Supported languages:{Style.RESET_ALL}")

    for language in languages:
        lang = get_language_context(language)
        s.writeln(f"  {blue(language)} - {lang.language_display_name}")

    return s.get_data()

