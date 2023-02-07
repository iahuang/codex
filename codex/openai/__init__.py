from codex.openai.interface import APIInterface
from codex.openai.prompts import InsertionPrompt, CompletionPrompt, BasePrompt

CODEX_MODEL = "code-davinci-002"
API_BASE = "https://api.openai.com/v1/"
DAVINCI_MAX_TOKENS = 4000


class OpenAICodexError(Exception):
    pass


class OpenAI:
    api_key: str
    _api: APIInterface

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self._api = APIInterface(base_url=API_BASE, authorization_header="Bearer " + api_key)

    def generate_code(self, prompt: BasePrompt, temperature: float, target_max_tokens: int) -> str:
        """
        Generate code using OpenAI Codex, and return the generated code (not including the prompt).

        `target_max_tokens` is the strict maximum number of tokens to generate. If set to `0`,
        generate as many tokens as the model will allow, as determined by the size of the prompt.
        The model may generate fewer tokens if the prompt is too long, but the output
        length will never exceed `target_max_tokens`.

        `temperature` is the temperature to use for the generation. Higher values will result in
        more random output, while lower values will result in more predictable output. For
        Codex, the recommended range is 0.0 to 0.2.

        Raise an `OpenAICodexError` if the API returns an error.

        If the size of the prompt exceeds the maximum number of tokens allowed by the model,
        raise a `ValueError`.
        """

        if prompt.get_token_count() > DAVINCI_MAX_TOKENS:
            raise ValueError(
                f"The provided prompt is too long ({prompt.get_token_count()}/{DAVINCI_MAX_TOKENS} tokens)."
            )

        # determine the maximum number of tokens left for output, since the model input and
        # output combined cannot exceed a fixed number of tokens
        tokens_left = DAVINCI_MAX_TOKENS - prompt.get_token_count()

        # determine the max_tokens value to pass to the API; given as the smaller between
        # tokens_left and max_tokens unless max_tokens is NO_MAX_TOKENS
        if target_max_tokens == 0:
            max_tokens = tokens_left
        else:
            max_tokens = min(tokens_left, target_max_tokens)

        data = {
            "model": CODEX_MODEL,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stop": prompt.stop_sequences,
        }

        if isinstance(prompt, InsertionPrompt):
            data["prompt"] = prompt.prefix
            data["suffix"] = prompt.suffix
        elif isinstance(prompt, CompletionPrompt):
            data["prompt"] = prompt.prompt

        response = self._api.post("/completions", body=data)

        if "error" in response:
            raise OpenAICodexError(response["error"])

        return response["choices"][0]["text"]
