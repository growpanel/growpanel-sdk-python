"""GrowPanel API error type. Raised on non-2xx responses."""

from typing import Any


class GrowPanelError(Exception):
    """Raised when a GrowPanel API call returns a non-2xx status.

    Attributes:
        status: HTTP status code returned by the API.
        body: Parsed JSON body if the response was JSON, otherwise the raw text.
    """

    def __init__(self, status: int, status_text: str, body: Any) -> None:
        error_msg = None
        if isinstance(body, dict) and isinstance(body.get("error"), str):
            error_msg = body["error"]
        message = f"GrowPanel API {status}: {error_msg}" if error_msg else f"GrowPanel API {status} {status_text}"
        super().__init__(message)
        self.status = status
        self.status_text = status_text
        self.body = body
