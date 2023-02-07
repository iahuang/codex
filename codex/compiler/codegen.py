from dataclasses import dataclass
from typing import Iterable, Optional
from codex.compiler.language_binding import LanguageBinding
from codex.lang.types import Type
from codex.openai import DAVINCI_MAX_TOKENS
from codex.openai.prompts import BasePrompt, CompletionPrompt, InsertionPrompt, count_tokens
from codex.util.strings import StringBuilder

GENERATED = "{{GENERATED}}"


def ensure_trailing_newline(text: str) -> str:
    """
    Ensure that the given text ends with a newline.
    """

    if text.endswith("\n"):
        return text

    return text + "\n"


@dataclass
class SnippetBlueprint:
    """
    Dataclass returned by Codegen methods.

    Represents a method for generating a snippet of code: a prompt and a template. The prompt defines
    how the OpenAI Codex model should be queried, and the template defines how the
    result should be incorporated into the final code snippet.
    """

    codex_prompt: BasePrompt
    generation_template: str

    def generate(self, completion: str) -> str:
        """
        Generate a code snippet from the given completion.

        The completion is inserted into the template at the `GENERATED` placeholder.
        """

        return self.generation_template.replace(GENERATED, completion)


@dataclass
class CodegenContext:
    required_context: str
    """
    Code that is required to be present in the prompt. For instance,
    this might include library imports.
    """

    helpful_context: str
    """
    Code that is helpful to be present in the prompt. For instance,
    the code generated before the code being generated.
    """


RequiredUsages = Iterable[str]
"""
A collection of required usages for this context. The values returned by this method
correspond to the `given` field of an AI prompt, i.e. the symbols `a`, `b`, `c`, ... in
syntax of the form:
```
[a, b, c, ...]: <prompt>
```

This method should brief English descriptions of the required usages, e.g.
```
["the variable A", "the function B", "the class C", ...]
```
"""


class Codegen:
    language: LanguageBinding
    token_limit: int
    _context: Optional[CodegenContext]

    def __init__(self, language: LanguageBinding, prompt_token_limit: int) -> None:
        self.language = language
        self._context = None
        self.token_limit = prompt_token_limit

    def set_context(self, context: CodegenContext) -> None:
        self._context = context

    def build_contextualized_prompt(self, prompt: BasePrompt) -> BasePrompt:
        if not self._context:
            return prompt

        # prepend the language name to the required context
        lang_header = self.language.generate_single_line_comment(self.language.info.display_name)
        required_context = (
            ensure_trailing_newline(lang_header)
            + "\n"
            + ensure_trailing_newline(self._context.required_context)
        )

        # see how many tokens we have left to work with
        required_tokens = count_tokens(required_context)
        tokens_left = self.token_limit - required_tokens

        if tokens_left <= 0:
            raise ValueError("The required context provided is too long.")

        # build the prompt by prepending the required context to a prompt that
        # has been truncated to fit within the token limit adjusted for the
        # required context.

        if isinstance(prompt, CompletionPrompt):
            new_prompt = prompt.clone()
            new_prompt.prompt = (
                ensure_trailing_newline(self._context.helpful_context) + prompt.prompt
            )
            new_prompt.truncate_prompt(tokens_left)
            new_prompt.prompt = required_context + new_prompt.prompt

            return new_prompt

        if isinstance(prompt, InsertionPrompt):
            new_prompt = prompt.clone()
            new_prompt.prefix = (
                ensure_trailing_newline(self._context.helpful_context) + prompt.prefix
            )
            new_prompt.truncate_prompt(tokens_left)
            new_prompt.prefix = required_context + new_prompt.prefix

            return new_prompt

        raise ValueError(f"Unknown prompt type: {type(prompt)}")

    def generate_action(self, action_prompt: str) -> SnippetBlueprint:
        """
        Example template output for a prompt such as "print the sum of a and b":
        ```
        # print the sum of a and b
        {{GENERATED}}
        ```
        """

        prompt = CompletionPrompt(
            prompt=self.language.generate_single_line_comment(action_prompt) + "\n"
        )
        prompt.set_stop_sequences(["\n\n"])

        template = StringBuilder()
        template.writeln(self.language.generate_single_line_comment(action_prompt))
        template.writeln(GENERATED)

        return SnippetBlueprint(
            codex_prompt=self.build_contextualized_prompt(prompt),
            generation_template=template.to_string(),
        )

    def generate_variable_decl(
        self, name: str, type: Optional[Type], variable_prompt: str
    ) -> SnippetBlueprint:
        """
        Example template output:
        ```
        # the sum of b and c
        a: int = {{GENERATED}}
        ```
        """

        # e.g. "int a = "
        stub = self.language.generate_incomplete_variable_assignment(name, type)
        variable_description = self.language.generate_single_line_comment(variable_prompt)

        # e.g.
        # "// the sum of a and b
        # int a = "
        prompt = CompletionPrompt(
            prompt=variable_description + "\n" + stub,
        )
        prompt.set_stop_sequences(["\n\n"])

        # construct template

        template = StringBuilder()
        # add original prompt as a comment
        template.writeln(self.language.generate_single_line_comment(variable_prompt))
        # add variable declaration
        template.writeln(self.language.generate_variable_assignment(name, type, GENERATED))

        return SnippetBlueprint(
            codex_prompt=self.build_contextualized_prompt(prompt),
            generation_template=template.to_string(),
        )
