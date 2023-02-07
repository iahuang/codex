"""
Syntax grammar definitions for the Codex language.
"""

from typing import Optional
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
L_PAREN = Literal("(")
R_PAREN = Literal(")")
EXCLAMATION_MARK = Literal("!")
NON_EMPTY_TEXT = Regex(r".{0,}\S.{0,}").with_name("non-empty text")
COMMA = Literal(",")

# compound group names

GROUP_PROMPT = "prompt"
GROUP_PROMPT_TEXT = "prompt_text"
GROUP_PARAMETERS = "parameters"
GROUP_TYPE_NAME = "type_name"
GROUP_OPTIONAL_TYPE = "optional_type"
GROUP_SYMBOL_NAME = "symbol_name"

# component macros

COMPONENT_OPT_WHITESPACE = ExprComponent(WHITESPACE, optional=True)
COMPONENT_REQ_WHITESPACE = ExprComponent(WHITESPACE, optional=False)

COMPONENT_OPT_TYPE = ExprComponent(
    CompoundExpression(
        [ExprComponent(SYMBOL_NAME, group_name=GROUP_TYPE_NAME), COMPONENT_REQ_WHITESPACE]
    ),
    group_name=GROUP_OPTIONAL_TYPE,
    optional=True,
)


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
        COMPONENT_OPT_TYPE,
        ExprComponent(SYMBOL_NAME, group_name=GROUP_SYMBOL_NAME),
        COMPONENT_OPT_WHITESPACE,
        COMPONENT_PROMPT,
    ]
)
"""
Syntax:
```
var <type_name?> <variable_name> [<parameter_name>, ...]: <prompt_text>
```
"""

UsingDirective = CompoundExpression(
    [
        ExprComponent(Literal("using")),
        COMPONENT_REQ_WHITESPACE,
        ExprComponent(SYMBOL_NAME, group_name="module_name"),
    ]
)
"""
Syntax:
```
using <module_name>
```
"""

_FuncArgumentNonLast = CompoundExpression(
    [
        COMPONENT_OPT_WHITESPACE,
        COMPONENT_OPT_TYPE,
        ExprComponent(SYMBOL_NAME, group_name=GROUP_SYMBOL_NAME),
        COMPONENT_OPT_WHITESPACE,
        ExprComponent(COMMA),
    ]
)

_FuncArgumentLast = CompoundExpression(
    [
        COMPONENT_OPT_WHITESPACE,
        COMPONENT_OPT_TYPE,
        ExprComponent(SYMBOL_NAME, group_name=GROUP_SYMBOL_NAME),
        COMPONENT_OPT_WHITESPACE,
    ]
)

_FuncSomeArguments = CompoundExpression(
    [
        ExprComponent(L_PAREN),
        ExprComponent(Repeated(_FuncArgumentNonLast, min_count=0), group_name="non_last_arguments"),
        ExprComponent(_FuncArgumentLast, group_name="last_argument"),
        ExprComponent(R_PAREN),
    ]
)

_FuncNoArguments = CompoundExpression(
    [
        ExprComponent(L_PAREN),
        COMPONENT_OPT_WHITESPACE,
        ExprComponent(R_PAREN),
    ]
)

_FuncArguments = UnionExpression([_FuncSomeArguments, _FuncNoArguments])

PromptedFunctionDeclaration = CompoundExpression(
    [
        ExprComponent(Literal("fn")),
        COMPONENT_REQ_WHITESPACE,
        COMPONENT_OPT_TYPE,
        ExprComponent(SYMBOL_NAME, group_name=GROUP_SYMBOL_NAME),  # function name
        COMPONENT_OPT_WHITESPACE,
        ExprComponent(_FuncArguments, group_name="arguments"),
        COMPONENT_OPT_WHITESPACE,
        COMPONENT_PROMPT,
    ]
)
"""
Syntax:
```
fn <type_name?> <function_name>() <prompt>
```
"""

### Helper functions ###


def extract_function_arguments(match: MatchResult) -> list[tuple[str, Optional[str]]]:
    """
    Extract the argument names and optional type names from the given function match,
    as returned from `_FuncArguments`.

    Return a list of tuples of the argument name and the type name, or `None` if no type.
    """

    arguments = []

    if non_last_arguments_match := match.get_named_group_optional("non_last_arguments"):
        for argument_match in non_last_arguments_match.indexed_groups:
            arguments.append(extract_symbol_decl_info(argument_match))

    if last_argument_match := match.get_named_group("last_argument"):
        arguments.append(extract_symbol_decl_info(last_argument_match))

    return arguments


def extract_symbol_decl_info(match: MatchResult) -> tuple[str, Optional[str]]:
    """
    Extract the symbol name and optional type name from a compound match object
    containing group names `GROUP_SYMBOL_NAME` and component `OPT_TYPE`, for instance,
    `VariableDeclaration` and `_FuncArgumentLast` matches.

    Return a tuple of the variable name and the type name, or `None` if no type.
    """

    variable_name = match.get_named_group(GROUP_SYMBOL_NAME).matched_string

    type_name = None

    if type_match := match.get_named_group_optional(GROUP_OPTIONAL_TYPE):
        type_name = type_match.get_named_group(GROUP_TYPE_NAME).matched_string

    return variable_name, type_name


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
