class StringBuilder:
    _data: str

    def __init__(self) -> None:
        self._data = ""

    def write(self, data: str) -> None:
        self._data += data

    def writeln(self, data="") -> None:
        self.write(data + "\n")

    def to_string(self, trim_trailing_whitespace=False) -> str:
        if trim_trailing_whitespace:
            return self._data.rstrip()
        else:
            return self._data

    def clear(self) -> None:
        self._data = ""


def indented(code: str, indentation_spaces: int = 4) -> str:
    """
    Indents the given code by the given number of spaces.

    Example:
    ```
    print(indented("a\\nb\\nc", 2)) # prints "  a\\n  b\\n  c"
    ```
    """

    return "\n".join(" " * indentation_spaces + line for line in code.split("\n"))
