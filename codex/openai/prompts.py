from __future__ import annotations
from transformers import GPT2Tokenizer

TOKENIZER: GPT2Tokenizer = GPT2Tokenizer.from_pretrained("gpt2")


def count_tokens(text: str) -> int:
    """
    Return the number of tokens in the given text.
    """

    return len(TOKENIZER.encode(text))


class BasePrompt:
    stop_sequences: list[str]

    def __init__(self, stop_sequences: list[str] = []) -> None:
        self.stop_sequences = stop_sequences

    def set_stop_sequences(self, stop_sequences: list[str]) -> None:
        self.stop_sequences = stop_sequences

    def get_stop_sequences(self) -> list[str]:
        return self.stop_sequences

    def get_token_count(self) -> int:
        """
        Return the number of tokens in the prompt via GPT-2 tokenizer.
        """

        raise NotImplementedError

    def truncate_prompt(self, max_tokens: int) -> None:
        """
        Modify the prompt in-place such that it is no longer than `max_tokens` tokens.
        """

        raise NotImplementedError

    def clone(self) -> BasePrompt:
        """
        Return a copy of the prompt.
        """

        raise NotImplementedError


class CompletionPrompt(BasePrompt):
    prompt: str

    def __init__(self, prompt: str) -> None:
        super().__init__()

        self.prompt = prompt

    def get_token_count(self) -> int:
        return count_tokens(self.prompt)

    def truncate_prompt(self, max_tokens: int) -> None:
        """
        Truncate the prompt by removing tokens from the start of the prompt.
        """

        # encode the prompt to get the token IDs
        token_ids = TOKENIZER.encode(self.prompt)

        # if the prompt is already short enough, do nothing
        if len(token_ids) <= max_tokens:
            return

        # remove tokens from the start of the prompt until it is short enough
        while len(token_ids) > max_tokens:
            token_ids.pop(0)

        # decode the token IDs back into text
        self.prompt = TOKENIZER.decode(token_ids)

    def clone(self) -> CompletionPrompt:
        clone = CompletionPrompt(self.prompt)
        clone.set_stop_sequences(self.get_stop_sequences())

        return clone


class InsertionPrompt(BasePrompt):
    prefix: str
    suffix: str
    min_prefix_tokens: int
    min_suffix_tokens: int

    def __init__(self, prefix: str, suffix: str) -> None:
        super().__init__()

        self.prefix = prefix
        self.suffix = suffix

        self.min_prefix_tokens = 0
        self.min_suffix_tokens = 0

    def get_token_count(self) -> int:
        return count_tokens(self.prefix) + count_tokens(self.suffix)

    def set_truncation_settings(self, min_prefix_tokens: int, min_suffix_tokens: int) -> None:
        """
        Set the minimum number of tokens that must be present in the prefix and suffix
        when truncating the prompt.
        """

        self.min_prefix_tokens = min_prefix_tokens
        self.min_suffix_tokens = min_suffix_tokens

    def truncate_prompt(self, max_tokens: int) -> None:
        """
        Truncate the prompt by first attempting to remove from the start of the prefix,
        then from the end of the suffix.

        The minimum number of tokens that must be present in the prefix and suffix
        may be set via `set_truncation_settings`.

        If the combined minimum number of tokens is greater than `max_tokens`, raise
        a ValueError.
        """

        prefix_tokens = TOKENIZER.encode(self.prefix)
        suffix_tokens = TOKENIZER.encode(self.suffix)

        # if the prompt is already short enough, do nothing
        if len(prefix_tokens) + len(suffix_tokens) <= max_tokens:
            return

        # if the combined minimum number of tokens is greater than `max_tokens`, raise
        # a ValueError
        if self.min_prefix_tokens + self.min_suffix_tokens > max_tokens:
            raise ValueError("The combined minimum number of tokens is greater than `max_tokens`.")

        # remove tokens from the start of the prefix until it is short enough
        while (
            len(prefix_tokens) + len(suffix_tokens) > max_tokens
            and len(prefix_tokens) > self.min_prefix_tokens
        ):
            prefix_tokens.pop(0)

        # remove tokens from the end of the suffix until it is short enough
        while (
            len(prefix_tokens) + len(suffix_tokens) > max_tokens
            and len(suffix_tokens) > self.min_suffix_tokens
        ):
            suffix_tokens.pop(0)

        # decode the token IDs back into text
        self.prefix = TOKENIZER.decode(prefix_tokens)
        self.suffix = TOKENIZER.decode(suffix_tokens)

    def clone(self) -> InsertionPrompt:
        prompt = InsertionPrompt(self.prefix, self.suffix)
        prompt.set_truncation_settings(self.min_prefix_tokens, self.min_suffix_tokens)
        prompt.set_stop_sequences(self.get_stop_sequences())
        return prompt
