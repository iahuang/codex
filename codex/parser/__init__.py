from codex.parser.ast import Module
from codex.parser.parser import Parser
from codex.parser.source import CodexSource

def parse(source: CodexSource) -> Module:
    """
    Parse the given Codex source code and return a corresponding AST representation.
    """

    parser = Parser(source)
    return parser.parse()

def parse_string(source: str) -> Module:
    """
    Parse the given Codex source code and return a corresponding AST representation.
    """

    return parse(CodexSource.from_string(source))