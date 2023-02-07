"""
Syntax grammar definitions for the Codex language.
"""

from codex.parser.ast import PromptData
from codex.parser.grammar import (
    CompoundExpression,
    ExprComponent,
    MatchResult,
    Repeated,
    Literal,
    Regex,
    UnionExpression,
)

### Macros ###

# basic symbols and expressions

WHITESPACE = Regex(r"\s+").with_name("whitespace")
SYMBOL_NAME = Regex(r"\w+").with_name("symbol name")
SQ_BRACKET_OPEN = Literal("[")
SQ_BRACKET_CLOSE = Literal("]")
EXCLAMATION_MARK = Literal("!")
NON_EMPTY_TEXT = Regex(r".{0,}\S.{0,}").with_name("non-empty text")
COMMA = Literal(",")

# compound group names

GROUP_PROMPT = "prompt"
GROUP_PROMPT_TEXT = "prompt_text"
GROUP_PARAMETERS = "parameters"

# component macros

COMPONENT_OPT_WHITESPACE = ExprComponent(WHITESPACE, optional=True)
COMPONENT_REQ_WHITESPACE = ExprComponent(WHITESPACE, optional=False)

### Expressions ###

_AIGenerativeParameterNonLast = CompoundExpression(
    [
        COMPONENT_OPT_WHITESPACE,
        ExprComponent(SYMBOL_NAME, group_name="symbol_name"),
        COMPONENT_OPT_WHITESPACE,
        ExprComponent(COMMA),
    ]
).with_name("non-last parameter")

_AIGenerativeParameterLast = CompoundExpression(
    [
        COMPONENT_OPT_WHITESPACE,
        ExprComponent(SYMBOL_NAME, group_name="symbol_name"),
        COMPONENT_OPT_WHITESPACE,
    ]
).with_name("last parameter")

_AIGenerativeParametersMultiple = CompoundExpression(
    [
        ExprComponent(SQ_BRACKET_OPEN),
        ExprComponent(
            Repeated(_AIGenerativeParameterNonLast, min_count=0), group_name="non_last_parameters"
        ),
        ExprComponent(_AIGenerativeParameterLast, group_name="last_parameter"),
        ExprComponent(SQ_BRACKET_CLOSE),
    ]
).with_name("multiple parameters")
"""
Syntax:
```
[<parameter_name>, ..., <parameter_name>]
```
"""

_AIGenerativeParametersSingle = CompoundExpression(
    [
        ExprComponent(SQ_BRACKET_OPEN),
        ExprComponent(_AIGenerativeParameterLast, group_name="last_parameter"),
        ExprComponent(SQ_BRACKET_CLOSE),
    ]
).with_name("single parameter")
"""
Syntax:
```
[<parameter_name>]
```
"""

AIPrompt = CompoundExpression(
    [
        ExprComponent(
            UnionExpression([_AIGenerativeParametersMultiple, _AIGenerativeParametersSingle]),
            group_name=GROUP_PARAMETERS,
            optional=True,
        ),
        COMPONENT_OPT_WHITESPACE,
        ExprComponent(Literal(":")),
        COMPONENT_OPT_WHITESPACE,
        ExprComponent(NON_EMPTY_TEXT, group_name=GROUP_PROMPT_TEXT),
    ]
).with_name("generative statement")
"""
Syntax:
```
[<parameter_name>, ...]: <prompt_text>
```
"""

COMPONENT_PROMPT = ExprComponent(AIPrompt, group_name=GROUP_PROMPT)

ActionStatement = CompoundExpression(
    [
        ExprComponent(EXCLAMATION_MARK),
        COMPONENT_OPT_WHITESPACE,
        COMPONENT_PROMPT,
    ]
).with_name("action statement")
"""
Syntax:
```
! [<parameter_name>, ...]: <prompt_text>
```
"""

VariableDeclaration = CompoundExpression(
    [
        ExprComponent(Literal("var")),
        COMPONENT_REQ_WHITESPACE,
        ExprComponent(SYMBOL_NAME, group_name="type_name"),
        COMPONENT_REQ_WHITESPACE,
        ExprComponent(SYMBOL_NAME, group_name="variable_name"),
        COMPONENT_OPT_WHITESPACE,
        COMPONENT_PROMPT,
    ]
)
"""
Syntax:
```
var <type_name> <variable_name> [<parameter_name>, ...]: <prompt_text>
```
"""

UsingDirective = CompoundExpression(
    [
        ExprComponent(Literal("using")),
        COMPONENT_REQ_WHITESPACE,
        ExprComponent(SYMBOL_NAME, group_name="module_name"),
    ]
)

### Helper functions ###


def get_parameter_names(parameter_match: MatchResult) -> list[str]:
    """
    Extract the symbol names from the given parameter match, as returned from
    `UnionExpression([_AIGenerativeParametersMultiple, _AIGenerativeParametersSingle])`.
    """

    last_symbol_name = (
        parameter_match.get_named_group("last_parameter")
        .get_named_group("symbol_name")
        .matched_string
    )

    non_last_symbol_names: list[str] = []

    if non_last := parameter_match.get_named_group_optional("non_last_parameters"):
        for param in non_last.indexed_groups:
            non_last_symbol_names.append(param.get_named_group("symbol_name").matched_string)

    return non_last_symbol_names + [last_symbol_name]


def extract_prompt(match: MatchResult) -> PromptData:
    """
    Extract relevant information from a match object as returned from `AIPrompt`.
    """

    text = match.get_named_group(GROUP_PROMPT_TEXT).matched_string
    parameter_match = match.get_named_group_optional(GROUP_PARAMETERS)
    given = None

    if parameter_match:
        given = get_parameter_names(parameter_match)

    return PromptData(text, given or [])


def extract_module_name(match: MatchResult) -> str:
    """
    Extract the module name from a match object as returned from `UsingDirective`.
    """

    return match.get_named_group("module_name").matched_string
