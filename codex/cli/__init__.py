import argparse
import os

from sys import stderr
from pathlib import Path
from typing import Optional
from codex.compiler.config import CompilerConfig, CompilerConfigError, validate_config
from codex.parser import parse
from codex.parser.errors import CodexSyntaxError
from codex.parser.source import CodexSource
from codex.compiler import Compiler
from codex.compiler.targets import LANGUAGE_REGISTRY
from codex.cli.formatting import (
    MODE_ERROR,
    MODE_WARNING,
    format_compileerror,
    format_compilerconfigerror,
    format_syntaxerror,
    format_language_list,
    format_simple_error,
    red,
    yellow,
)
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
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="The output file to write to, or the destination directory if the path given to -o is a directory.",
    )
    parser.add_argument(
        "--target",
        type=str,
        help="The language to compile to (default: python3)",
        default="python3",
    )
    parser.add_argument(
        "-e", "--env", type=str, help="Path to an alternate .env file", default=".env"
    )
    parser.add_argument(
        "--list-languages", action="store_true", help="List all supported target languages"
    )
    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        help="The temperature to use for code generation. A number closer to zero produces less interesting, but more reliable output. (default: 0.05)",
        default=0.05,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose output to the console",
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
        # if no output path is specified, use the name of the input file
        output_path = Path(args.filename).name.split(".")[0]

    return CompilerConfig(
        target_language_name=args.target,
        openai_key=openai_key,
        temperature=args.temperature,
        verbose=args.verbose,
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
        print(format_language_list(LANGUAGE_REGISTRY))
        print()
        return

    if not args.filename:
        stderr_print(format_simple_error("No input file specified. Use -h for help."))
        return

    try:
        config = args_as_compiler_config(args)
        validate_config(config)

        source = CodexSource.from_file(args.filename)
        module = parse(source)

        compiler = Compiler(module, config)
        compiler.compile()

        output_path = args.output

        # if the output file is a directory, use the name of the input file
        # appended to the directory, minus the extension
        if os.path.isdir(output_path):
            output_path = os.path.join(output_path, Path(args.filename).name.split(".")[0])

        # if no output path is specified, use the name of the input file
        if not output_path:
            output_path = Path(args.filename).name.split(".")[0]

        # if the output file lacks an extension, add the extension of the target language
        if not Path(output_path).suffix:
            output_path += "." + compiler.target.info.source_file_extension

        with open(output_path, "w") as f:
            f.write(compiler.get_output())

        for error in compiler.get_errors():
            stderr_print(format_compileerror(error, MODE_ERROR))
            stderr_print()

        for warning in compiler.get_warnings():
            stderr_print(format_compileerror(warning, MODE_WARNING))
            stderr_print()

        num_errs = len(compiler.get_errors())
        emsg = red(str(num_errs) + " error" + ("s" if num_errs > 1 else ""))
        num_warns = len(compiler.get_warnings())
        wmsg = yellow(str(num_warns) + " warning" + ("s" if num_warns > 1 else ""))

        if num_errs > 0 and num_warns == 0:
            stderr_print(f"Compilation failed with {emsg}.")
        elif num_errs == 0 and num_warns > 0:
            stderr_print(f"Compilation succeeded with {wmsg}.")
        elif num_errs > 0 and num_warns > 0:
            stderr_print(f"Compilation failed with {emsg} and {wmsg}.")

    except CompilerConfigError as e:
        stderr_print(format_compilerconfigerror(e))
    except CodexSyntaxError as e:
        stderr_print(format_syntaxerror(e))
