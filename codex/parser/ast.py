from dataclasses import dataclass

SymbolName = str


class ASTNode:
    def __init__(self) -> None:
        pass


class AIGenerative(ASTNode):
    given: list[SymbolName]
    prompt: str

    def __init__(self, prompt: str, given: list[SymbolName] = []) -> None:
        self.prompt = prompt
        self.given = given


class ActionStatementNode(AIGenerative):
    pass


class CodeBlock(ASTNode):
    children: list[ASTNode]

    def __init__(self, children: list[ASTNode] = []) -> None:
        self.children = children

class Module(CodeBlock):
    pass