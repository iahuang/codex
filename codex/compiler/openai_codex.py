from codex.compiler.prompt_generation import InsertPrompt
from codex.util.fs import write_json
from transformers import GPT2Tokenizer
import json
import requests

NO_MAX_TOKENS = 0
API_BASE = "https://api.openai.com/v1/"
MODEL_MAX_TOKENS = 4000


def url_join(base: str, *components: str) -> str:
    """
    Example:
    ```
    >>> url_join("http://example.com/", "api", "/v3/test")
    'http://example.com/api/v3/test'
    ```
    """

    return base.rstrip("/") + "/" + "/".join(c.strip("/") for c in components)


class OpenAICodexError(Exception):
    pass

class OpenAICodex:
    api_key: str
    _model: str
    _tokenizer: GPT2Tokenizer

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key

        self._tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self._model = model

    def _get_token_count(self, text: str) -> int:
        return len(self._tokenizer.encode(text))

    def generate_insertion(self, prompt: InsertPrompt, temperature: float, max_tokens: int) -> str:
        """
        Generate code insertion using OpenAI Codex.

        `max_tokens` is the maximum number of tokens to generate. If set to `NO_MAX_TOKENS`,
        generate as many tokens as the model will allow, as determined by the size of the prompt.

        `temperature` is the temperature to use for the generation. Higher values will result in
        more random output, while lower values will result in more predictable output. For
        Codex, the recommended range is 0.0 to 0.2.
        """

        # determine the maximum number of tokens left for output, since the model input and
        # output combined cannot exceed a fixed number of tokens
        tokens_left = MODEL_MAX_TOKENS - self._get_token_count(prompt.prefix + prompt.suffix)

        # determine the max_tokens value to pass to the API; given as the smaller between
        # tokens_left and max_tokens unless max_tokens is NO_MAX_TOKENS
        api_tokens = tokens_left if max_tokens == NO_MAX_TOKENS else min(tokens_left, max_tokens)

        response = requests.post(
            url=url_join(API_BASE, "/completions"),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.api_key},
            data=json.dumps(
                {
                "model": self._model,
                "prompt": prompt.prefix,
                "suffix": prompt.suffix,
                "max_tokens": api_tokens,
                "temperature": temperature,
            }),
        )

        data = response.json()

        if "error" in data:
            raise OpenAICodexError(data["error"])
        
        generation = data["choices"][0]["text"]

        # trim leading newlines from the generation
        return generation.lstrip("\n")