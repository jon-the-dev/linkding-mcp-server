"""Pydantic models for LinkDing API responses."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Bookmark(BaseModel):
    """Represents a LinkDing bookmark."""

    id: int
    url: str
    title: str
    description: str = ""
    notes: str = ""
    web_archive_snapshot_url: Optional[str] = None
    favicon_url: Optional[str] = None
    preview_image_url: Optional[str] = None
    is_archived: bool = False
    unread: bool = False
    shared: bool = False
    tag_names: List[str] = []
    date_added: str
    date_modified: str


class BookmarkList(BaseModel):
    """Represents a paginated list of bookmarks."""

    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Bookmark]


class Tag(BaseModel):
    """Represents a LinkDing tag."""

    id: int
    name: str
    date_added: str


class TagList(BaseModel):
    """Represents a paginated list of tags."""

    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Tag]


class BookmarkCheck(BaseModel):
    """Represents the result of checking if a URL is bookmarked."""

    bookmark: Optional[Bookmark] = None
    metadata: Dict[str, Any] = {}
    auto_tags: List[str] = []
