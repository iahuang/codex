import os
from typing import Union, Any
import shutil
import json


def read_file(path: str) -> str:
    """Return the contents of a file as a string"""
    with open(path) as fl:
        return fl.read()


def write_file(path: str, data: Union[str, bytes]) -> None:
    """
    Write data to a file, creating it and its parent directories if necessary.
    Overrite the file if it already exists.
    """

    if not os.path.exists(os.path.dirname(path)) and os.path.dirname(path) != "":
        os.makedirs(os.path.dirname(path))

    is_bytes = isinstance(data, bytes)

    with open(path, "wb" if is_bytes else "w") as fl:
        fl.write(data)


def write_json(path: str, data: Any) -> None:
    """
    Write JSON data to a file, creating it and its parent directories if necessary.
    Overrite the file if it already exists.
    """

    write_file(path, data=json.dumps(data))


def _is_line_empty(line: str) -> bool:
    """Return true if the given string is empty or only whitespace"""

    return len(line.strip()) == 0


def read_file_as_lines(path: str, remove_blank_lines: bool = False) -> list[str]:
    """Return the contents of the files as a list of lines"""
    
    data = read_file(path)
    lines = data.split("\n")

    if not remove_blank_lines:
        return lines

    return [line for line in lines if not _is_line_empty(line)]


def remove_path(path: str, ignore_if_missing: bool = False) -> None:
    """Delete the file or folder at [path], empty or not."""

    if not os.path.exists(path) and not ignore_if_missing:
        raise FileNotFoundError('File at "{}" was not found.'.format(path))

    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)
