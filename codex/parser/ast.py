from dataclasses import dataclass

SymbolName = str


class ASTNode:
    def __init__(self) -> None:
        pass


class AIGenerative(ASTNode):
    given: list[SymbolName]

    def __init__(self, given: list[SymbolName] = []) -> None:
        self.given = given


class ActionStatement(AIGenerative):
    pass


class CodeBlock(ASTNode):
    children: list[ASTNode]

    def __init__(self, children: list[ASTNode] = []) -> None:
        self.children = children

class Module(CodeBlock):
    pass