from typing import NoReturn, Optional
from dataclasses import dataclass

from codex.parser.errors import CodexSyntaxError
from codex.parser.syntax import (
    ActionStatement,
    UsingDirective,
    VariableDeclaration,
    extract_prompt,
    extract_module_name,
    GROUP_PROMPT,
)
from codex.parser.source import CodexSource
from codex.parser.ast import (
    Location,
    Module,
    ASTNode,
    ActionStatementNode,
    UsingDirectiveNode,
    VariableDeclarationNode,
)
from codex.parser.grammar import identify_string, ExpressionMatchError


# Measured in spaces OR tabs
IndentationLevel = int


def is_blank_string(s: str) -> bool:
    """
    Return `True` if the given string is empty or contains only whitespace characters.
    """

    return s.strip() == ""


class Parser:
    """
    This class implements the Codex parser.

    It is not intended to be used directly. Instead, use the `parse` function.
    """

    source: CodexSource
    current_line_idx: int

    def __init__(self, source: CodexSource) -> None:
        self.current_line_idx = 0
        self.source = source

    def get_current_line(self) -> str:
        """
        Return the current line.
        """

        return self.source.get_line_by_index(self.current_line_idx)

    def get_current_line_number(self) -> int:
        """
        Return the current line number, starting at 1.
        """

        return self.current_line_idx + 1

    def at_end(self) -> bool:
        """
        Return whether the parser is at the end of the source code.
        """

        return self.current_line_idx >= self.source.get_line_count()

    def next_line(self) -> Optional[str]:
        """
        Increment the current line index and return the new current line, or None if there is no next line.
        """

        self.current_line_idx += 1

        if self.at_end():
            return None

        return self.get_current_line()

    def _get_current_source_location(self) -> Location:
        return Location(self.source, self.get_current_line_number())

    def parse_current_line(
        self, enclosing_indentation_level: IndentationLevel
    ) -> Optional[tuple[ASTNode, IndentationLevel]]:
        """
        Parse the current line and return the a tuple, where the first element is an AST node
        representing the current line, and the second element is the indentation level of the
        current line.

        If there is no semantic meaning to the current line, e.g. an empty line, return None.
        """

        line = self.get_current_line()

        # ignore blank lines

        if is_blank_string(line):
            return None

        indentation, trimmed_line = self.get_indentation_of_current_line()

        # ignore comments

        if trimmed_line.startswith("//"):
            return None

        # validate indentation

        if indentation > enclosing_indentation_level:
            self.raise_syntax_error_at_current_line(
                "Unexpected indentation",
                note=f"Expected indentation level of {enclosing_indentation_level}, got {indentation}",
            )

        # identify the statement type, raising an error if it could not be identified

        identified_expr = identify_string(
            trimmed_line, [ActionStatement, VariableDeclaration, UsingDirective]
        )

        if identified_expr is None:
            self.raise_syntax_error_at_current_line(
                f"Unrecognized token {trimmed_line.split(' ')[0]!r}"
            )

        # parse the statement

        location = self._get_current_source_location()

        try:
            match = identified_expr.match(trimmed_line, throw_on_failure=True)
            assert match is not None

            if identified_expr == ActionStatement:
                prompt = extract_prompt(match.get_named_group(GROUP_PROMPT))
                node = ActionStatementNode(location, prompt)

                return node, indentation

            if identified_expr == VariableDeclaration:
                variable_name = match.get_named_group("variable_name").matched_string
                type_name = match.get_named_group("type_name").matched_string
                prompt = extract_prompt(match.get_named_group(GROUP_PROMPT))

                node = VariableDeclarationNode(location, variable_name, type_name, prompt)

                return node, indentation

            if identified_expr == UsingDirective:
                module_name = extract_module_name(match)

                return UsingDirectiveNode(location, module_name), indentation

        except ExpressionMatchError as e:
            self.raise_syntax_error_at_current_line(e.message)

        raise NotImplementedError(
            f"AST node for {identified_expr.human_representation()} not implemented yet."
        )

    def parse(self) -> Module:
        """
        Parse the source code provided to the constructor and return a corresponding AST
        representation. This is the main entry point of the parser, and this method may only
        be called once.
        """

        module = Module(self._get_current_source_location())

        while not self.at_end():
            parse_result = self.parse_current_line(0)

            if parse_result is not None:
                module.children.append(parse_result[0])

            self.next_line()

        return module

    def raise_syntax_error_at_current_line(
        self, message: str, note: Optional[str] = None
    ) -> NoReturn:
        """
        Raise a `CodexSyntaxError` at the current line.
        """

        raise CodexSyntaxError(self.source, self.get_current_line_number(), message, note)

    def get_indentation_of_current_line(self) -> tuple[IndentationLevel, str]:
        """
        Return a tuple where the first element is the indentation level of the current line,
        and the second element is the line without the indentation.

        The indentation level is measured in spaces OR tabs.
        Mixed indentation is not allowed. If the line is empty, the indentation level is 0.
        """

        line = self.get_current_line()

        MODE_UNASSIGNED = 0
        MODE_SPACES = 1
        MODE_TABS = 2

        indentation_level = 0
        indentation_mode = 0

        for char in line:
            if char == " ":
                if indentation_mode == MODE_UNASSIGNED:
                    indentation_mode = MODE_SPACES
                elif indentation_mode == MODE_TABS:
                    self.raise_syntax_error_at_current_line(
                        "Mixed indentation is not allowed.",
                        note="Line starts with a tab, but contains spaces.",
                    )

                indentation_level += 1
            elif char == "\t":
                if indentation_mode == MODE_UNASSIGNED:
                    indentation_mode = MODE_TABS
                elif indentation_mode == MODE_SPACES:
                    self.raise_syntax_error_at_current_line(
                        "Mixed indentation is not allowed.",
                        note="Line starts with a space, but contains tabs.",
                    )

                indentation_level += 1
            else:
                break

        return indentation_level, line[indentation_level:]
