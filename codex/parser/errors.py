from typing import Optional
from codex.parser.source import CodexSource


class CodexSyntaxError(Exception):
    message: str
    note: Optional[str]
    line: int
    source: CodexSource

    def __init__(self, source: CodexSource, line: int, message: str, note: Optional[str] = None) -> None:
        self.message = message
        self.line = line
        self.source = source
        self.note = note