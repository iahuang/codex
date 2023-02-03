from __future__ import annotations

class CodexSource:
    _content: str
    _lines: list[str]

    def __init__(self, from_string: str) -> None:
        """
        Initialize a Codex source object from the given string. Windows line endings will be
        converted to Unix line endings.
        """

        # force Unix line endings
        from_string = from_string.replace("\r\n", "\n")

        self._content = from_string
        self._lines = from_string.split("\n")
    
    @staticmethod
    def from_file(path: str) -> CodexSource:
        """
        Read the source from the given file path.
        """

        with open(path, "r") as f:
            return CodexSource(f.read())
    
    def get_line_by_index(self, index: int) -> str:
        """
        Return the line at the given index.
        """

        return self._lines[index]
    
    def get_line_by_number(self, number: int) -> str:
        """
        Return the line at the given number, starting at 1.
        """

        return self._lines[number - 1]
    
    def get_line_count(self) -> int:
        """
        Return the number of lines in the source.
        """

        return len(self._lines)
    
    def is_line_number_valid(self, number: int) -> bool:
        """
        Return whether the given line number is valid.
        """

        return number > 0 and number <= self.get_line_count()
    
    def is_line_index_valid(self, index: int) -> bool:
        """
        Return whether the given line index is valid.
        """

        return index >= 0 and index < self.get_line_count()
