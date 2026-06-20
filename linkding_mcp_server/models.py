"""Pydantic models for LinkDing data structures"""

from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, HttpUrl, field_validator


def normalize_tag(v: str) -> str:
    """Normalize and validate a single tag name"""
    if not v:
        raise ValueError("Tag name cannot be empty")
    if len(v) > 100:
        raise ValueError("Tag name must be 100 characters or less")
    # Allow alphanumeric, hyphens, underscores, and dots
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
    if not all(c in allowed_chars for c in v):
        raise ValueError("Tag name can only contain letters, numbers, hyphens, underscores, and dots")
    return v.lower()  # Normalize to lowercase


def normalize_tags(v: list[str] | None) -> list[str] | None:
    """Normalize a list of tags"""
    if v is None:
        return v
    return [normalize_tag(tag) for tag in v if tag]


def clean_text(v: str | None) -> str | None:
    """Clean and normalize text fields"""
    if v:
        # Remove excessive whitespace
        v = " ".join(v.split())
        # Strip leading/trailing whitespace
        v = v.strip()
    return v


# Type aliases with validators
NormalizedTags = Annotated[list[str] | None, BeforeValidator(normalize_tags)]
CleanedText = Annotated[str | None, BeforeValidator(clean_text)]


class BookmarkBase(BaseModel):
    """Base bookmark model with validation"""

    url: HttpUrl = Field(..., description="The URL of the bookmark")
    title: CleanedText = Field(None, max_length=500, description="Bookmark title")
    description: CleanedText = Field(None, max_length=2000, description="Bookmark description")
    notes: CleanedText = Field(None, max_length=5000, description="Personal notes")
    tags: NormalizedTags = Field(default_factory=list, max_length=50, description="List of tags")
    is_archived: bool = Field(default=False, description="Archive status")
    unread: bool = Field(default=False, description="Unread status")
    shared: bool = Field(default=False, description="Shared status")


class Bookmark(BookmarkBase):
    """Complete bookmark model from API response"""

    id: int
    web_archive_snapshot_url: str | None = None
    favicon_url: HttpUrl | None = None
    preview_image_url: HttpUrl | None = None
    tag_names: list[str] = Field(default_factory=list)
    date_added: datetime
    date_modified: datetime

    model_config = ConfigDict(
        populate_by_name=True,
    )


class BookmarkCreate(BookmarkBase):
    """Model for creating a new bookmark"""

    url: HttpUrl = Field(..., description="The URL to bookmark (required)")

    @field_validator("url", mode="before")
    @classmethod
    def validate_url_not_empty(cls, v):
        """Ensure URL is not empty"""
        if not v or str(v).strip() == "":
            raise ValueError("URL cannot be empty")
        return v


class BookmarkUpdate(BaseModel):
    """Model for updating a bookmark"""

    url: HttpUrl | None = None
    title: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=5000)
    tags: NormalizedTags = Field(None, max_length=50)
    is_archived: bool | None = None
    unread: bool | None = None
    shared: bool | None = None


class BookmarkList(BaseModel):
    """Paginated list of bookmarks"""

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[Bookmark]


class Tag(BaseModel):
    """LinkDing tag model"""

    id: int
    name: str = Field(..., max_length=100)
    date_added: datetime

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate tag name"""
        if not v:
            raise ValueError("Tag name cannot be empty")
        return v.lower()


class TagList(BaseModel):
    """Paginated list of tags"""

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[Tag]


class BookmarkCheck(BaseModel):
    """Result of checking if a URL is bookmarked"""

    bookmark: Bookmark | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    auto_tags: list[str] = Field(default_factory=list)


class SearchParams(BaseModel):
    """Validated search parameters"""

    query: str | None = Field(None, max_length=500, description="Search query")
    tag: str | None = Field(None, max_length=100, description="Tag filter")
    limit: int = Field(default=100, ge=1, le=1000, description="Results limit")
    offset: int = Field(default=0, ge=0, description="Results offset")
    archived: bool = Field(default=False, description="Search archived bookmarks")
    unread_only: bool = Field(default=False, description="Only unread bookmarks")

    @field_validator("tag")
    @classmethod
    def validate_tag(cls, v):
        """Validate and normalize tag"""
        if v:
            return v.lower()
        return v
