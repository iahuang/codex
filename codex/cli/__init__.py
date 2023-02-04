import argparse
from sys import stderr
from pathlib import Path
from typing import Optional
from codex.parser import parse
from codex.parser.source import CodexSource
from codex.compiler import CompilerConfig, CompilerConfigError, Compiler
from codex.compiler.languages import get_all_languages
from codex.cli.formatting import format_compilerconfigerror, format_language_list, format_simple_error
from dotenv import dotenv_values


def get_arg_parser() -> argparse.ArgumentParser:
    """
    Return the argument parser for the CLI.
    """

    parser = argparse.ArgumentParser(
        prog="codex",
        description="A concept programming language powered by the OpenAI model of the same name.",
    )

    parser.add_argument(
        "filename", type=str, help="The source file to compile", nargs="?", default=None
    )
    parser.add_argument("-o", "--output", type=str, help="The output file to write to")
    parser.add_argument(
        "-l", "--language", type=str, help="The language to compile to", default="python3"
    )
    parser.add_argument("-e", "--env", type=str, help="Path to the .env file", default=".env")
    parser.add_argument(
        "--list-languages", action="store_true", help="List all supported target languages"
    )

    return parser


def args_as_compiler_config(args: argparse.Namespace) -> CompilerConfig:
    """
    Return a CompilerConfig object from the given arguments as parsed by the argument parser.
    """

    env_config = dotenv_values(args.env)

    openai_key = env_config["OPENAI_KEY"]

    if not openai_key:
        raise CompilerConfigError("OPENAI_KEY is not set in the .env file.")

    output_path: str = args.output

    if not args.output:
        output_path = Path(args.filename).name.split(".")[0]

    return CompilerConfig(
        language_name=args.language,
        output_path=output_path,
        openai_key=openai_key,
    )


def stderr_print(*args, **kwargs) -> None:
    """
    Print to stderr.
    """

    print(*args, file=stderr, **kwargs)


def run_cli() -> None:
    """
    Main entry point for the CLI.
    """

    parser = get_arg_parser()
    args = parser.parse_args()

    if args.list_languages:
        print()
        print(format_language_list(get_all_languages()))
        print()
        return
    
    if not args.filename:
        stderr_print(format_simple_error("No input file specified. Use -h for help."))
        return

    try:
        config = args_as_compiler_config(args)
        source = CodexSource.from_file(args.filename)
        module = parse(source)

        compiler = Compiler(module, config)
        compiler.compile()
    except CompilerConfigError as e:
        stderr_print(format_compilerconfigerror(e))
