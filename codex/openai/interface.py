from typing import Any, Dict, List, Optional, Union
import requests


def url_join(base: str, *components: str) -> str:
    """
    Join a base URL with a list of components, ensuring that there is exactly one
    slash between each component.

    Example:
    ```
    >>> url_join("http://example.com/", "api", "/v3/test")
    'http://example.com/api/v3/test'
    ```
    """

    return base.rstrip("/") + "/" + "/".join(c.strip("/") for c in components)


class APIInterface:
    base_url: str
    authorization_header: str

    def __init__(self, base_url: str, authorization_header: str) -> None:
        self.base_url = base_url
        self.authorization_header = authorization_header

    def post(self, endpoint: str, body: Any) -> dict:
        """
        Perform a POST request to the API. The `body` parameter is automatically
        JSON-serialized.

        The `Authorization` header is automatically set to the
        value of `self.authorization_header`, and the `Content-Type` header is
        automatically set to `application/json`.

        Return the JSON response.
        """

        return requests.post(
            url_join(self.base_url, endpoint),
            json=body,
            headers={
                "Authorization": self.authorization_header,
                "Content-Type": "application/json",
            },
        ).json()

    def get(self, endpoint: str, query: dict[str, str]) -> dict:
        """
        Perform a GET request to the API. The `query` parameter is automatically
        URL-encoded.

        The `Authorization` header is automatically set to the
        value of `self.authorization_header`, and the `Content-Type` header is
        automatically set to `application/json`.

        Return the JSON response.
        """

        return requests.get(
            url_join(self.base_url, endpoint),
            params=query,
            headers={
                "Authorization": self.authorization_header,
                "Content-Type": "application/json",
            },
        ).json()
