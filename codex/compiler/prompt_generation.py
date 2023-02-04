from dataclasses import dataclass
from codex.compiler.language_context import BaseLanguageContext
from codex.parser.ast import ActionStatementNode
from codex.util import StringBuilder

@dataclass
class InsertPrompt:
    prefix: str
    suffix: str = ""

class PromptGenerator:
    lang: BaseLanguageContext

    def __init__(self, language_context: BaseLanguageContext) -> None:
        self.lang = language_context

    def action_statement(self, action: ActionStatementNode) -> InsertPrompt:
        """
        Generate a Codex prompt for generating code corresponding to the given action statement.
        """

        header = self.lang.generate_single_line_comment(self.lang.language_display_name)
        comment = self.lang.generate_multi_line_comment(action.prompt)

        s = StringBuilder()
        s.writeln(header)
        s.writeln()
        s.writeln(comment)

        return InsertPrompt(s.get_data())
