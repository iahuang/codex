from dataclasses import dataclass
from typing import Optional
from codex.parser.source import CodexSource

SymbolName = str


@dataclass
class Location:
    source: CodexSource
    line_no: int


class ASTNode:
    location: Location

    def __init__(self, location: Location) -> None:
        self.location = location


@dataclass
class PromptData:
    """
    Dataclass member of some AST nodes that represent an associated AI prompt.
    """

    prompt: str
    given: list[str]


class PromptNode(ASTNode):
    """
    Represents any AST node that contains a prompt.
    """

    prompt: PromptData

    def __init__(self, location: Location, prompt: PromptData) -> None:
        super().__init__(location)
        self.prompt = prompt


class ActionStatementNode(PromptNode):
    pass


class VariableDeclarationNode(PromptNode):
    variable_name: SymbolName
    type: Optional[str]

    def __init__(
        self,
        location: Location,
        name: SymbolName,
        type: Optional[str],
        prompt: PromptData,
    ) -> None:
        super().__init__(location, prompt)
        self.variable_name = name
        self.type = type


class UsingDirectiveNode(ASTNode):
    module_name: str

    def __init__(self, location: Location, module_name: str) -> None:
        super().__init__(location)
        self.module_name = module_name


class CodeBlock(ASTNode):
    children: list[ASTNode]

    def __init__(self, location: Location, children: list[ASTNode] = []) -> None:
        super().__init__(location)
        self.children = children


class Module(CodeBlock):
    pass
