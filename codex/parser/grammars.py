from codex.parser.grammar_parser import (
    CompoundExpression,
    ExprComponent,
    Repeated,
    Literal,
    Regex,
    UnionExpression,
)

WHITESPACE = Regex(r"\s+").with_name("whitespace")
SYMBOL_NAME = Regex(r"\w+")
SQ_BRACKET_OPEN = Literal("[")
SQ_BRACKET_CLOSE = Literal("]")
EXCLAMATION_MARK = Literal("!")
NON_EMPTY_TEXT = Regex(r".{0,}\S.{0,}").with_name("non-empty text")

COMMA = Literal(",")

OPTIONAL_WHITESPACE = ExprComponent(WHITESPACE, optional=True)

_AIGenerativeParameterNonLast = CompoundExpression(
    [
        OPTIONAL_WHITESPACE,
        ExprComponent(SYMBOL_NAME, group_name="symbol_name"),
        OPTIONAL_WHITESPACE,
        ExprComponent(COMMA),
    ]
).with_name("non-last parameter")

_AIGenerativeParameterLast = CompoundExpression(
    [
        OPTIONAL_WHITESPACE,
        ExprComponent(SYMBOL_NAME, group_name="symbol_name"),
        OPTIONAL_WHITESPACE,
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

_AIGenerativeParametersSingle = CompoundExpression(
    [
        ExprComponent(SQ_BRACKET_OPEN),
        ExprComponent(_AIGenerativeParameterLast, group_name="last_parameter"),
        ExprComponent(SQ_BRACKET_CLOSE),
    ]
).with_name("single parameter")

AIGenerativeStatement = CompoundExpression(
    [
        ExprComponent(
            UnionExpression([_AIGenerativeParametersMultiple, _AIGenerativeParametersSingle]),
            group_name="parameters",
            optional=True,
        ),
        OPTIONAL_WHITESPACE,
        ExprComponent(Literal(":")),
        OPTIONAL_WHITESPACE,
        ExprComponent(NON_EMPTY_TEXT, group_name="statement_text"),
    ]
).with_name("generative statement")

ActionStatement = CompoundExpression(
    [
        ExprComponent(EXCLAMATION_MARK),
        OPTIONAL_WHITESPACE,
        ExprComponent(AIGenerativeStatement, group_name="generative_statement"),
    ]
).with_name("action statement")
