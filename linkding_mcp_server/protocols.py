"""Public structural interfaces for LinkDing client implementations."""

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Any, Protocol, Self, TypeVar, runtime_checkable

from linkding_mcp_server.config import Settings
from linkding_mcp_server.models import (
    Bookmark,
    BookmarkCheck,
    BookmarkCreate,
    BookmarkList,
    BookmarkUpdate,
    TagList,
)

ResultT = TypeVar("ResultT")


@runtime_checkable
class LinkDingClientProtocol(Protocol):
    """Operations exposed by an async LinkDing client."""

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    async def get_bookmarks(self, archived: bool = False, **params: Any) -> BookmarkList: ...

    async def create_bookmark(self, bookmark: BookmarkCreate) -> Bookmark: ...

    async def get_bookmark(self, bookmark_id: int) -> Bookmark: ...

    async def update_bookmark(self, bookmark_id: int, update: BookmarkUpdate) -> Bookmark: ...

    async def delete_bookmark(self, bookmark_id: int) -> bool: ...

    async def archive_bookmark(self, bookmark_id: int) -> bool: ...

    async def unarchive_bookmark(self, bookmark_id: int) -> bool: ...

    async def check_url(self, url: str) -> BookmarkCheck: ...

    async def get_tags(self, limit: int = 100, offset: int = 0) -> TagList: ...

    def paginate_results(
        self,
        endpoint: str,
        model_class: Callable[..., ResultT],
        params: dict[str, Any],
        max_results: int | None = None,
        max_pages: int | None = None,
    ) -> AsyncIterator[ResultT]: ...


ClientFactory = Callable[
    [Settings],
    AbstractAsyncContextManager[LinkDingClientProtocol],
]
