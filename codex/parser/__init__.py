from typing import Optional
from .ast import ASTNode, Module

def is_blank_string(s: str) -> bool:
    """
    Return `True` if the given string is empty or contains only whitespace characters.
    """

    return s.strip() == ""

class _Parser:
    """
    This class implements the Codex parser.

    It is not intended to be used directly. Instead, use the `parse` function.
    """

    source: str
    lines: list[str]
    current_line_idx: int

    def __init__(self, source: str) -> None:
        # force Unix line endings
        source = source.replace("\r\n", "\n")

        self.source = source
        self.lines = source.split("\n")
        self.current_line_idx = 0

    def get_current_line(self) -> str:
        """
        Return the current line.
        """

        return self.lines[self.current_line_idx]

    def at_end(self) -> bool:
        """
        Return whether the parser is at the end of the source code.
        """

        return self.current_line_idx >= len(self.lines)

    def next_line(self) -> Optional[str]:
        """
        Increment the current line index and return the new current line, or None if there is no next line.
        """

        self.current_line_idx += 1

        if self.at_end():
            return None

        return self.get_current_line()
    
    def parse_current_line(self) -> Optional[ASTNode]:
        """
        Parse the current line and return the corresponding AST node.

        If there is no semantic meaning to the current line, e.g. an empty line, return None.
        """

        line = self.get_current_line()

        if is_blank_string(line): return None
        
        
    def parse(self) -> Module:
        module = Module()

        while not self.at_end():
            node = self.parse_current_line()
            
            if node is not None:
                module.children.append(node)

        return module


def parse(source: str) -> Module:
    """
    Parse the given Codex source code and return a corresponding AST representation.
    """

    parser = _Parser(source)
    return parser.parse()
