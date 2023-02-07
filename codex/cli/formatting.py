from colorama import Fore, Style
from codex.compiler.compiler import CompilerError
from codex.compiler.config import CompilerConfigError
from codex.compiler.language_binding import LanguageBinding
from codex.parser.errors import CodexSyntaxError
from codex.parser.source import CodexSource
from codex.util.strings import StringBuilder


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


def dim(text: str) -> str:
    """
    Return the given text in dim.
    """

    return f"{Style.DIM}{text}{Style.RESET_ALL}"


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


def _get_source_preview(source: CodexSource, line_no: int) -> str:
    return f"{dim(str(line_no)+ '| '+source.get_line_by_number(line_no))}"


def format_syntaxerror(error: CodexSyntaxError) -> str:
    """
    Format the given CodexSyntaxError as a colored string.
    """

    s = StringBuilder()
    s.writeln(f"at {blue(error.source.get_name())}, line {error.line_no}")

    # preview the line where the error occurred
    s.writeln(_get_source_preview(error.source, error.line_no))
    s.writeln()

    s.writeln(f"{red('syntax error:')} {error.message}")

    return s.to_string(trim_trailing_whitespace=True)


MODE_ERROR = 0
MODE_WARNING = 1


def format_compileerror(error: CompilerError, mode: int) -> str:
    """
    Format the given error as a colored string.
    """

    source = error.offending_node.location.source
    line_no = error.offending_node.location.line_no

    s = StringBuilder()
    s.writeln(f"at {blue(source.get_name())}, line {line_no}")

    # preview the line where the error occurred
    s.writeln(_get_source_preview(source, line_no))

    if mode == MODE_ERROR:
        s.writeln(f"{red('error:')} {error.message}")
    elif mode == MODE_WARNING:
        s.writeln(f"{yellow('warning:')} {error.message}")

    return s.to_string(trim_trailing_whitespace=True)


def format_language_list(languages: list[LanguageBinding]) -> str:
    """
    Format the given list of language names as a colored string.
    """

    s = StringBuilder()
    s.writeln(f"{Style.BRIGHT}Supported languages:{Style.RESET_ALL}")

    for lang in languages:
        s.writeln(f"  {blue(lang.name)} - {lang.info.display_name}")
        s.writeln(f"    {dim(lang.info.description)}")
        s.writeln()

    return s.to_string(trim_trailing_whitespace=True)
