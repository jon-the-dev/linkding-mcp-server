"""HTTP client wrapper for the LinkDing REST API."""

import httpx

from linkding_mcp_server.config import Settings


async def handle_api_error(response: httpx.Response) -> str:
    """Parse an error response and return a human-readable message.

    Args:
        response: The failed HTTP response.

    Returns:
        A descriptive error string.
    """
    try:
        error_data = response.json()
        if isinstance(error_data, dict):
            if "detail" in error_data:
                return f"API Error: {error_data['detail']}"
            elif "error" in error_data:
                return f"API Error: {error_data['error']}"
            else:
                return f"API Error: {error_data}"
        else:
            return f"API Error: {error_data}"
    except Exception:
        return f"HTTP {response.status_code}: {response.text}"


class LinkDingClient:
    """Thin async HTTP client for the LinkDing API.

    Args:
        settings: Runtime configuration containing the base URL and token.
    """

    def __init__(self, settings: Settings) -> None:
        self._http = httpx.AsyncClient(
            base_url=f"{settings.linkding_url}/api",
            headers={"Authorization": f"Token {settings.api_token}"},
            timeout=30.0,
        )

    async def get(self, path: str, **kwargs) -> httpx.Response:
        """Delegate a GET request to the underlying HTTP client."""
        return await self._http.get(path, **kwargs)

    async def post(self, path: str, **kwargs) -> httpx.Response:
        """Delegate a POST request to the underlying HTTP client."""
        return await self._http.post(path, **kwargs)

    async def patch(self, path: str, **kwargs) -> httpx.Response:
        """Delegate a PATCH request to the underlying HTTP client."""
        return await self._http.patch(path, **kwargs)

    async def delete(self, path: str, **kwargs) -> httpx.Response:
        """Delegate a DELETE request to the underlying HTTP client."""
        return await self._http.delete(path, **kwargs)

    async def aclose(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()
