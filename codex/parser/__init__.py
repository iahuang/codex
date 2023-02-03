from .ast import Module
from .parser import Parser

def parse(source: str) -> Module:
    """
    Parse the given Codex source code and return a corresponding AST representation.
    """

    parser = Parser(source)
    return parser.parse()
