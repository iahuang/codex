"""
Implementation of a basic non-recursive grammar parser.
"""

from __future__ import annotations
import re
from typing import Optional
from dataclasses import dataclass, field


def but_got(remaining: str) -> str:
    if len(remaining) == 0:
        return "EOF"

    return f"{remaining[0]!r}"


class ExpressionMatchError(Exception):
    string: str
    """
    The string that was being matched against, and which failed to match.
    """

    message: str

    def __init__(self, string: str, message: str) -> None:
        self.string = string
        self.message = message


@dataclass
class MatchResult:
    matched_string: str
    named_groups: dict[str, MatchResult] = field(default_factory=dict)
    indexed_groups: list[MatchResult] = field(default_factory=list)

    def get_match_length(self) -> int:
        return len(self.matched_string)

    def has_named_group(self, name: str) -> bool:
        return name in self.named_groups

    def get_named_group(self, name: str) -> MatchResult:
        if name not in self.named_groups:
            raise ValueError(f"Named group {name} does not exist")

        return self.named_groups[name]

    def get_named_group_optional(self, name: str) -> Optional[MatchResult]:
        if name not in self.named_groups:
            return None

        return self.named_groups[name]

    def get_indexed_group(self, index: int) -> MatchResult:
        if index >= len(self.indexed_groups):
            raise ValueError(f"Indexed group {index} does not exist")

        return self.indexed_groups[index]


class Expression:
    name: Optional[str]

    def __init__(self) -> None:
        self.name = None

    def match(self, string: str, throw_on_failure=False) -> Optional[MatchResult]:
        """
        Returns a MatchResult object if this expression matches `string`, and `None` otherwise.
        """

        raise NotImplementedError

    def with_name(self, name: str):  # return type intentionally omitted, as to be inferred
        """
        Set the name of this expression. This is used for producing a human-readable representation
        of the expression, when necessary.
        """

        self.name = name

        return self

    def human_representation(self) -> str:
        """
        Return a human-readable representation of this expression, for use in
        error messages. If the expression has a name, that name should be returned instead.
        """

        return self.name if self.name else "[Expression]"


class Literal(Expression):
    literal: str
    case_sensitive: bool

    def __init__(self, literal: str, case_sensitive=True) -> None:
        super().__init__()
        self.literal = literal
        self.case_sensitive = case_sensitive

    def match(self, string: str, throw_on_failure=False) -> Optional[MatchResult]:
        if self.case_sensitive:
            if string.startswith(self.literal):
                return MatchResult(self.literal)
        else:
            if string.lower().startswith(self.literal.lower()):
                return MatchResult(string[: len(self.literal) + 1])

        if throw_on_failure:
            raise ExpressionMatchError(
                string, f"Expected {self.human_representation()}, but got {but_got(string)}"
            )

        return None

    def human_representation(self) -> str:
        if self.name:
            return self.name

        return repr(self.literal)


class Regex(Expression):
    regex: str

    def __init__(self, regex: str) -> None:
        super().__init__()
        self.regex = regex

    def match(self, string: str, throw_on_failure=False) -> Optional[MatchResult]:
        match = re.match(self.regex, string)
        if match:
            return MatchResult(match.group())

        if throw_on_failure:
            raise ExpressionMatchError(
                string, f"Expected {self.human_representation()}, but got {but_got(string)}"
            )

        return None

    def human_representation(self) -> str:
        if self.name:
            return self.name

        return f"/{self.regex}/"


@dataclass
class ExprComponent:
    expression: Expression
    optional: bool = False
    group_name: Optional[str] = None


@dataclass
class SoftMatchResult:
    match_result: Optional[MatchResult] = None
    num_parts_matched_successfully: int = 0

    def successful(self) -> bool:
        return self.match_result is not None


class CompoundExpression(Expression):
    components: list[ExprComponent]

    def __init__(self, components: list[ExprComponent]) -> None:
        super().__init__()
        self.components = components

        if len(self.components) == 0:
            raise ValueError("CompoundExpression must have at least one component.")

        # check that there are no duplicate group names

        group_names = set()

        for component in self.components:
            if component.group_name:
                if component.group_name in group_names:
                    raise ValueError(f"Duplicate group name {component.group_name}")

                group_names.add(component.group_name)

    def match(self, string: str, throw_on_failure=False) -> Optional[MatchResult]:
        soft_match = self.soft_match(string, throw_on_failure)

        if soft_match.successful():
            return soft_match.match_result

    def soft_match(self, string: str, throw_on_failure=False) -> SoftMatchResult:
        """
        Match as much of the string as possible, and return the number of parts that were
        matched successfully.
        """

        result: Optional[MatchResult] = MatchResult("")
        num_parts_matched_successfully = 0

        for component in self.components:
            match = component.expression.match(
                string, throw_on_failure=throw_on_failure and not component.optional
            )

            # if not component.optional: print(match, component.expression.human_representation(), "for", self.human_representation(), repr(result.matched_string))

            if match:
                result.matched_string += match.matched_string

                # remove the matched part from the string
                string = string[match.get_match_length() :]

                # capture named group, if applicable
                if component.group_name:
                    result.named_groups[component.group_name] = match

                num_parts_matched_successfully += 1
            elif not component.optional:
                if throw_on_failure:
                    raise ExpressionMatchError(
                        string,
                        f"Expected {component.expression.human_representation()}, but got {but_got(string)}",
                    )

                result = None
                break

        return SoftMatchResult(result, num_parts_matched_successfully)


class UnionExpression(Expression):
    expressions: list[Expression]

    def __init__(self, expressions: list[Expression]) -> None:
        """
        Expressions are tried in the order they are given.
        """

        super().__init__()
        self.expressions = expressions

        if len(self.expressions) == 0:
            raise ValueError("UnionExpression must have at least one expression.")

    def match(self, string: str, throw_on_failure=False) -> Optional[MatchResult]:
        for expression in self.expressions:
            match = expression.match(string, throw_on_failure=False)
            if match:
                return match

        if throw_on_failure:
            raise ExpressionMatchError(
                string, f"Expected {self.human_representation()}, but got {but_got(string)}"
            )

        return None

    def human_representation(self) -> str:
        if self.name:
            return self.name

        if len(self.expressions) == 1:
            return self.expressions[0].human_representation()

        if len(self.expressions) == 2:
            return f"{self.expressions[0].human_representation()} or {self.expressions[1].human_representation()}"

        return f"{', '.join(expression.human_representation() for expression in self.expressions[:-1])} ,or {self.expressions[-1].human_representation()}"


class Repeated(Expression):
    expression: Expression
    min_count: int
    max_count: Optional[int]

    def __init__(
        self, expression: Expression, min_count: int, max_count: Optional[int] = None
    ) -> None:
        super().__init__()
        self.expression = expression
        self.min_count = min_count
        self.max_count = max_count

        if self.min_count < 0:
            raise ValueError("min_count must be >= 0")

        if self.max_count is not None and self.max_count < self.min_count:
            raise ValueError("max_count must be >= min_count")

    def match(self, string: str, throw_on_failure=False) -> Optional[MatchResult]:
        result = MatchResult("")
        count = 0

        while True:
            match = self.expression.match(string, throw_on_failure)
            if match:
                result.matched_string += match.matched_string
                result.indexed_groups.append(match)
                string = string[match.get_match_length() :]
                count += 1
            else:
                break

        if count < self.min_count:
            if throw_on_failure:
                raise ExpressionMatchError(
                    string,
                    f"Expected at least {self.min_count} matches of {self.expression.human_representation()}, but got {count}.",
                )

            return None

        if self.max_count is not None and count > self.max_count:
            if throw_on_failure:
                raise ExpressionMatchError(
                    string,
                    f"Expected at most {self.max_count} matches of {self.expression.human_representation()}, but got {count}.",
                )

            return None

        return result

    def human_representation(self) -> str:
        if self.name:
            return self.name

        if self.min_count == 0 and self.max_count == 1:
            return f"optional {self.expression.human_representation()}"

        if self.min_count == 0 and self.max_count is None:
            return f"zero or more {self.expression.human_representation()}"

        if self.min_count == 1 and self.max_count is None:
            return f"one or more {self.expression.human_representation()}"

        if self.min_count == 1 and self.max_count == 1:
            return f"exactly one {self.expression.human_representation()}"

        if self.max_count is None:
            return f"at least {self.min_count} {self.expression.human_representation()}"

        return f"between {self.min_count} and {self.max_count} {self.expression.human_representation()}"


def identify_string(
    string: str, candidate_expressions: list[CompoundExpression]
) -> Optional[CompoundExpression]:
    """
    Return the compound expression that matches the entire string succesfully, or if none match
    the entire string successfully, return the compound expression that matches the most
    components of the expression.

    Return `None` if no compound expression matches any compponents of the expression.
    """

    for expression in candidate_expressions:
        match = expression.soft_match(string)
        if match.successful():
            return expression

    best_match: Optional[CompoundExpression] = None
    best_match_num_parts_matched_successfully = 0

    for expression in candidate_expressions:
        match = expression.soft_match(string)
        if match.num_parts_matched_successfully > best_match_num_parts_matched_successfully:
            best_match = expression
            best_match_num_parts_matched_successfully = match.num_parts_matched_successfully

    return best_match
